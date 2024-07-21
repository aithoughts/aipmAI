def memoize(func):
    """
    一个装饰器，用于缓存函数的结果，避免重复计算。
    """
    cache = {}

    def memoized_func(*args, **kwargs):
        key = (args, tuple(kwargs.items()))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]

    memoized_func.__dict__.update(func.__dict__)
    return memoized_func


def task(func):
    """
    一个装饰器，用于标记一个函数为任务。
    它还使用 memoize 装饰器缓存任务的结果。
    """
    if not hasattr(task, "registration_order"):
        task.registration_order = []

    func.is_task = True
    wrapped_func = memoize(func)

    # 将函数名追加到注册顺序列表中
    task.registration_order.append(func.__name__)

    return wrapped_func


def agent(func):
    """
    一个装饰器，用于标记一个函数为代理。
    它还使用 memoize 装饰器缓存代理的结果。
    """
    func.is_agent = True
    func = memoize(func)
    return func


def crew(func):
    """
    一个装饰器，用于标记一个类为 Crew。
    它实例化所有标记为 @task 和 @agent 的方法，并将它们存储在 self.tasks 和 self.agents 中。
    """
    def wrapper(self, *args, **kwargs):
        instantiated_tasks = []
        instantiated_agents = []

        agent_roles = set()
        all_functions = {
            name: getattr(self, name)
            for name in dir(self)
            if callable(getattr(self, name))
        }
        tasks = {
            name: func
            for name, func in all_functions.items()
            if hasattr(func, "is_task")
        }
        agents = {
            name: func
            for name, func in all_functions.items()
            if hasattr(func, "is_agent")
        }

        # 按注册顺序对任务进行排序
        sorted_task_names = sorted(
            tasks, key=lambda name: task.registration_order.index(name)
        )

        # 按定义顺序实例化任务
        for task_name in sorted_task_names:
            task_instance = tasks[task_name]()
            instantiated_tasks.append(task_instance)
            if hasattr(task_instance, "agent"):
                agent_instance = task_instance.agent
                if agent_instance.role not in agent_roles:
                    instantiated_agents.append(agent_instance)
                    agent_roles.add(agent_instance.role)

        # 实例化所有尚未包含在任务中的其他代理
        for agent_name in agents:
            temp_agent_instance = agents[agent_name]()
            if temp_agent_instance.role not in agent_roles:
                instantiated_agents.append(temp_agent_instance)
                agent_roles.add(temp_agent_instance.role)

        self.agents = instantiated_agents
        self.tasks = instantiated_tasks

        return func(self, *args, **kwargs)

    return wrapper