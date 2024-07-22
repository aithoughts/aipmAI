import asyncio
import json
import uuid
from concurrent.futures import Future
from hashlib import md5
from typing import Any, Dict, List, Optional, Tuple, Union

from langchain_core.callbacks import BaseCallbackHandler
from pydantic import (
    UUID4,
    BaseModel,
    ConfigDict,
    Field,
    InstanceOf,
    Json,
    PrivateAttr,
    field_validator,
    model_validator,
)
from pydantic_core import PydanticCustomError

from crewai.agent import Agent
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.agents.cache import CacheHandler
from crewai.crews.crew_output import CrewOutput
from crewai.memory.entity.entity_memory import EntityMemory
from crewai.memory.long_term.long_term_memory import LongTermMemory
from crewai.memory.short_term.short_term_memory import ShortTermMemory
from crewai.process import Process
from crewai.task import Task
from crewai.tasks.conditional_task import ConditionalTask
from crewai.tasks.task_output import TaskOutput
# from crewai.telemetry import Telemetry
from crewai.tools.agent_tools import AgentTools
from crewai.utilities import I18N, FileHandler, Logger, RPMController
from crewai.utilities.constants import (
    TRAINED_AGENTS_DATA_FILE,
    TRAINING_DATA_FILE,
)
from crewai.utilities.evaluators.task_evaluator import TaskEvaluator
from crewai.utilities.formatter import (
    aggregate_raw_outputs_from_task_outputs,
    aggregate_raw_outputs_from_tasks,
)
from crewai.utilities.planning_handler import CrewPlanner
from crewai.utilities.task_output_storage_handler import TaskOutputStorageHandler
from crewai.utilities.training_handler import CrewTrainingHandler

try:
    import agentops
except ImportError:
    agentops = None


class Crew(BaseModel):
    """
     Crew 代表一组代理，定义它们如何协作以及它们应该执行的任务。

    属性：
        tasks: 分配给 Crew 的任务列表。
        agents: 属于此 Crew 的代理列表。
        manager_llm: 将运行管理代理的语言模型。
        manager_agent: 将用作管理器的自定义代理。
        memory:  Crew 是否应该使用记忆来存储其执行的记忆。
        manager_callbacks: 当使用分层流程时，管理代理在执行时要执行的回调处理程序
        cache:  Crew 是否应该使用缓存来存储工具执行的结果。
        function_calling_llm: 将为所有代理运行工具调用的语言模型。
        process:  Crew 将遵循的流程流（例如，顺序、分层）。
        verbose: 指示执行期间日志记录的详细程度。
        config:  Crew 的配置设置。
        max_rpm:  Crew 执行要遵守的最大每分钟请求数。
        prompt_file: 将用于 Crew 的提示 JSON 文件的路径。
        id:  Crew 实例的唯一标识符。
        task_callback: 在每个代理执行的每个任务之后执行的回调。
        step_callback: 在每个代理执行的每个步骤之后执行的回调。
        share_crew: 是否要与 crewAI 共享完整的 Crew 信息和执行，以使库更好，并允许我们训练模型。
        planning: 计划 Crew 执行并将计划添加到 Crew 。
    """

    __hash__ = object.__hash__  # type: ignore
    # _execution_span: Any = PrivateAttr()
    _rpm_controller: RPMController = PrivateAttr()
    _logger: Logger = PrivateAttr()
    _file_handler: FileHandler = PrivateAttr()
    _cache_handler: InstanceOf[CacheHandler] = PrivateAttr(default=CacheHandler())
    _short_term_memory: Optional[InstanceOf[ShortTermMemory]] = PrivateAttr()
    _long_term_memory: Optional[InstanceOf[LongTermMemory]] = PrivateAttr()
    _entity_memory: Optional[InstanceOf[EntityMemory]] = PrivateAttr()
    _train: Optional[bool] = PrivateAttr(default=False)
    _train_iteration: Optional[int] = PrivateAttr()
    _inputs: Optional[Dict[str, Any]] = PrivateAttr(default=None)
    _logging_color: str = PrivateAttr(
        default="bold_purple",
    )
    _task_output_handler: TaskOutputStorageHandler = PrivateAttr(
        default_factory=TaskOutputStorageHandler
    )

    cache: bool = Field(default=True)
    model_config = ConfigDict(arbitrary_types_allowed=True)
    tasks: List[Task] = Field(default_factory=list)
    agents: List[BaseAgent] = Field(default_factory=list)
    process: Process = Field(default=Process.sequential)
    verbose: Union[int, bool] = Field(default=0)
    memory: bool = Field(
        default=False,
        description=" Crew 是否应该使用记忆来存储其执行的记忆",
    )
    embedder: Optional[dict] = Field(
        default={"provider": "openai"},
        description="用于 Crew 的嵌入器的配置。",
    )
    usage_metrics: Optional[dict] = Field(
        default=None,
        description="在所有任务执行期间的 LLM 使用情况的指标。",
    )
    manager_llm: Optional[Any] = Field(
        description="将运行代理的语言模型。", default=None
    )
    manager_agent: Optional[BaseAgent] = Field(
        description="将用作管理器的自定义代理。", default=None
    )
    manager_callbacks: Optional[List[InstanceOf[BaseCallbackHandler]]] = Field(
        default=None,
        description="当使用分层流程时，管理代理要执行的回调处理程序列表",
    )
    function_calling_llm: Optional[Any] = Field(
        description="将运行代理的语言模型。", default=None
    )
    config: Optional[Union[Json, Dict[str, Any]]] = Field(default=None)
    id: UUID4 = Field(default_factory=uuid.uuid4, frozen=True)
    share_crew: Optional[bool] = Field(default=False)
    step_callback: Optional[Any] = Field(
        default=None,
        description="在所有代理执行的每个步骤之后执行的回调。",
    )
    task_callback: Optional[Any] = Field(
        default=None,
        description="在所有代理执行的每个任务之后执行的回调。",
    )
    max_rpm: Optional[int] = Field(
        default=None,
        description=" Crew 执行要遵守的最大每分钟请求数。",
    )
    prompt_file: str = Field(
        default=None,
        description="将用于 Crew 的提示 JSON 文件的路径。",
    )
    output_log_file: Optional[Union[bool, str]] = Field(
        default=False,
        description="output_log_file",
    )
    planning: Optional[bool] = Field(
        default=False,
        description="计划 Crew 执行并将计划添加到 Crew 。",
    )
    task_execution_output_json_files: Optional[List[str]] = Field(
        default=None,
        description="任务执行 JSON 文件的路径列表。",
    )
    execution_logs: List[Dict[str, Any]] = Field(
        default=[],
        description="任务的执行日志列表",
    )

    @field_validator("id", mode="before")
    @classmethod
    def _deny_user_set_id(cls, v: Optional[UUID4]) -> None:
        """防止用户手动设置 'id' 字段。"""
        if v:
            raise PydanticCustomError(
                "may_not_set_field", "用户无法设置 'id' 字段。", {}
            )

    @field_validator("config", mode="before")
    @classmethod
    def check_config_type(
        cls, v: Union[Json, Dict[str, Any]]
    ) -> Union[Json, Dict[str, Any]]:
        """验证配置是否为有效类型。
        参数：
            v: 要验证的配置。
        返回值：
            如果配置有效，则返回配置。
        """

        # TODO: 改善类型提示
        return json.loads(v) if isinstance(v, Json) else v  # type: ignore

    @model_validator(mode="after")
    def set_private_attrs(self) -> "Crew":
        """设置私有属性。"""
        self._cache_handler = CacheHandler()
        self._logger = Logger(self.verbose)
        if self.output_log_file:
            self._file_handler = FileHandler(self.output_log_file)
        self._rpm_controller = RPMController(max_rpm=self.max_rpm, logger=self._logger)
        # self._telemetry = Telemetry()
        # self._telemetry.set_tracer()
        return self

    @model_validator(mode="after")
    def create_crew_memory(self) -> "Crew":
        """设置私有属性。"""
        if self.memory:
            self._long_term_memory = LongTermMemory()
            self._short_term_memory = ShortTermMemory(
                crew=self, embedder_config=self.embedder
            )
            self._entity_memory = EntityMemory(crew=self, embedder_config=self.embedder)
        return self

    @model_validator(mode="after")
    def check_manager_llm(self):
        """验证使用分层流程时是否设置了语言模型。"""
        if self.process == Process.hierarchical:
            if not self.manager_llm and not self.manager_agent:
                raise PydanticCustomError(
                    "missing_manager_llm_or_manager_agent",
                    "使用分层流程时，`manager_llm` 或 `manager_agent` 属性是必需的。",
                    {},
                )

            if (self.manager_agent is not None) and (
                self.agents.count(self.manager_agent) > 0
            ):
                raise PydanticCustomError(
                    "manager_agent_in_agents",
                    "管理代理不应该包含在代理列表中。",
                    {},
                )

        return self

    @model_validator(mode="after")
    def check_config(self):
        """验证 Crew 是否使用代理和任务正确配置。"""
        if not self.config and not self.tasks and not self.agents:
            raise PydanticCustomError(
                "missing_keys",
                "需要设置 'agents' 和 'tasks'，或者设置 'config'。",
                {},
            )

        if self.config:
            self._setup_from_config()

        if self.agents:
            for agent in self.agents:
                if self.cache:
                    agent.set_cache_handler(self._cache_handler)
                if self.max_rpm:
                    agent.set_rpm_controller(self._rpm_controller)
        return self

    @model_validator(mode="after")
    def validate_tasks(self):
        if self.process == Process.sequential:
            for task in self.tasks:
                if task.agent is None:
                    raise PydanticCustomError(
                        "missing_agent_in_task",
                        f"顺序流程错误：在具有以下描述的任务中缺少代理：{task.description}",  # type: ignore # Argument of type "str" cannot be assigned to parameter "message_template" of type "LiteralString"
                        {},
                    )

        return self

    @model_validator(mode="after")
    def check_tasks_in_hierarchical_process_not_async(self):
        """验证分层流程中的任务没有标记为异步执行。"""
        if self.process == Process.hierarchical:
            for task in self.tasks:
                if task.async_execution:
                    raise PydanticCustomError(
                        "async_execution_in_hierarchical_process",
                        "分层流程错误：任务不能标记为异步执行。",
                        {},
                    )

        return self

    @model_validator(mode="after")
    def validate_end_with_at_most_one_async_task(self):
        """验证 Crew 最多以一个异步任务结束。"""
        final_async_task_count = 0

        # 反向遍历任务
        for task in reversed(self.tasks):
            if task.async_execution:
                final_async_task_count += 1
            else:
                break  # 遇到非异步任务时停止遍历

        if final_async_task_count > 1:
            raise PydanticCustomError(
                "async_task_count",
                " Crew 必须最多以一个异步任务结束。",
                {},
            )

        return self

    @model_validator(mode="after")
    def validate_first_task(self) -> "Crew":
        """确保第一个任务不是条件任务。"""
        if self.tasks and isinstance(self.tasks[0], ConditionalTask):
            raise PydanticCustomError(
                "invalid_first_task",
                "第一个任务不能是条件任务。",
                {},
            )
        return self

    @model_validator(mode="after")
    def validate_async_tasks_not_async(self) -> "Crew":
        """确保条件任务不是异步的。"""
        for task in self.tasks:
            if task.async_execution and isinstance(task, ConditionalTask):
                raise PydanticCustomError(
                    "invalid_async_conditional_task",
                    f"条件任务：{task.description}，不能异步执行。",  # type: ignore # Argument of type "str" cannot be assigned to parameter "message_template" of type "LiteralString"
                    {},
                )
        return self

    @model_validator(mode="after")
    def validate_async_task_cannot_include_sequential_async_tasks_in_context(self):
        """
        验证如果任务设置为异步执行，
        它不能在其上下文中包含其他异步任务，除非
        由同步任务分隔。
        """
        for i, task in enumerate(self.tasks):
            if task.async_execution and task.context:
                for context_task in task.context:
                    if context_task.async_execution:
                        for j in range(i - 1, -1, -1):
                            if self.tasks[j] == context_task:
                                raise ValueError(
                                    f"任务 '{task.description}' 是异步的，不能在其上下文中包含其他顺序异步任务。"
                                )
                            if not self.tasks[j].async_execution:
                                break
        return self

    @model_validator(mode="after")
    def validate_context_no_future_tasks(self):
        """验证任务的上下文不包含未来的任务。"""
        task_indices = {id(task): i for i, task in enumerate(self.tasks)}

        for task in self.tasks:
            if task.context:
                for context_task in task.context:
                    if id(context_task) not in task_indices:
                        continue  # 跳过不在主任务列表中的上下文任务
                    if task_indices[id(context_task)] > task_indices[id(task)]:
                        raise ValueError(
                            f"任务 '{task.description}' 对未来任务 '{context_task.description}' 有上下文依赖关系，这是不允许的。"
                        )
        return self

    @property
    def key(self) -> str:
        source = [agent.key for agent in self.agents] + [
            task.key for task in self.tasks
        ]
        return md5("|".join(source).encode()).hexdigest()

    def _setup_from_config(self):
        assert self.config is not None, "配置不能为空。"

        """从提供的配置初始化代理和任务。"""
        if not self.config.get("agents") or not self.config.get("tasks"):
            raise PydanticCustomError(
                "missing_keys_in_config", "配置应包含 'agents' 和 'tasks'。", {}
            )

        self.process = self.config.get("process", self.process)
        self.agents = [Agent(**agent) for agent in self.config["agents"]]
        self.tasks = [self._create_task(task) for task in self.config["tasks"]]
        
    def _create_task(self, task_config: Dict[str, Any]) -> Task:
        """从其配置创建任务实例。

        参数：
            task_config: 任务的配置。

        返回值：
            任务实例。
        """
        task_agent = next(
            agt for agt in self.agents if agt.role == task_config["agent"]
        )
        del task_config["agent"]
        return Task(**task_config, agent=task_agent)

    def _setup_for_training(self) -> None:
        """为训练设置 Crew 。"""
        self._train = True

        for task in self.tasks:
            task.human_input = True

        for agent in self.agents:
            agent.allow_delegation = False

        CrewTrainingHandler(TRAINING_DATA_FILE).initialize_file()
        CrewTrainingHandler(TRAINED_AGENTS_DATA_FILE).initialize_file()

    def train(self, n_iterations: int, inputs: Optional[Dict[str, Any]] = {}) -> None:
        """训练 Crew 一定数量的迭代。"""
        self._setup_for_training()

        for n_iteration in range(n_iterations):
            self._train_iteration = n_iteration
            self.kickoff(inputs=inputs)

        training_data = CrewTrainingHandler(TRAINING_DATA_FILE).load()

        for agent in self.agents:
            result = TaskEvaluator(agent).evaluate_training_data(
                training_data=training_data, agent_id=str(agent.id)
            )

            CrewTrainingHandler(TRAINED_AGENTS_DATA_FILE).save_trained_data(
                agent_id=str(agent.role), trained_data=result.model_dump()
            )

    def kickoff(
        self,
        inputs: Optional[Dict[str, Any]] = None,
    ) -> CrewOutput:
        """启动 Crew 以完成其分配的任务。"""
        # self._execution_span = self._telemetry.crew_execution_span(self, inputs)
        self._task_output_handler.reset()
        self._logging_color = "bold_purple"
        # 如果提供了输入，则设置输入并进行插值
        if inputs is not None:
            self._inputs = inputs
            self._interpolate_inputs(inputs)
        # 设置任务回调函数
        self._set_tasks_callbacks()
        # 初始化国际化
        i18n = I18N(prompt_file=self.prompt_file)
        # 遍历每个代理
        for agent in self.agents:
            # 设置代理的国际化和 Crew 实例
            agent.i18n = i18n
            # type: ignore[attr-defined] # Argument 1 to "_interpolate_inputs" of "Crew" has incompatible type "dict[str, Any] | None"; expected "dict[str, Any]"
            agent.crew = self  # type: ignore[attr-defined]
            # 如果代理没有设置函数调用LLM，则使用 Crew 的函数调用LLM
            if not agent.function_calling_llm:  # type: ignore # "BaseAgent" has no attribute "function_calling_llm"
                agent.function_calling_llm = self.function_calling_llm  # type: ignore # "BaseAgent" has no attribute "function_calling_llm"
            # 如果代理允许代码执行，则添加代码执行工具
            if agent.allow_code_execution:  # type: ignore # BaseAgent" has no attribute "allow_code_execution"
                agent.tools += agent.get_code_execution_tools()  # type: ignore # "BaseAgent" has no attribute "get_code_execution_tools"; maybe "get_delegation_tools"?
            # 如果代理没有设置步骤回调函数，则使用 Crew 的步骤回调函数
            if not agent.step_callback:  # type: ignore # "BaseAgent" has no attribute "step_callback"
                agent.step_callback = self.step_callback  # type: ignore # "BaseAgent" has no attribute "step_callback"
            # 创建代理执行器
            agent.create_agent_executor()
        # 如果启用了规划，则处理 Crew 规划
        if self.planning:
            self._handle_crew_planning()
        # 初始化指标列表
        metrics = []
        # 根据不同的处理流程执行任务
        if self.process == Process.sequential:
            result = self._run_sequential_process()
        elif self.process == Process.hierarchical:
            result = self._run_hierarchical_process()
        else:
            raise NotImplementedError(
                f"暂不支持 '{self.process}' 处理流程。"
            )
        # 收集指标数据
        metrics += [agent._token_process.get_summary() for agent in self.agents]
        # 汇总使用指标
        self.usage_metrics = {
            key: sum([m[key] for m in metrics if m is not None]) for key in metrics[0]
        }
        # 返回结果
        return result

    def kickoff_for_each(self, inputs: List[Dict[str, Any]]) -> List[CrewOutput]:
        """对列表中的每个输入执行 Crew 的工作流程，并聚合结果。"""
        results: List[CrewOutput] = []
        # 初始化父 Crew 的使用情况指标
        total_usage_metrics = {
            "total_tokens": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "successful_requests": 0,
        }

        for input_data in inputs:
            crew = self.copy()

            output = crew.kickoff(inputs=input_data)

            if crew.usage_metrics:
                for key in total_usage_metrics:
                    total_usage_metrics[key] += crew.usage_metrics.get(key, 0)

            results.append(output)

        self.usage_metrics = total_usage_metrics
        self._task_output_handler.reset()
        return results

    async def kickoff_async(self, inputs: Optional[Dict[str, Any]] = {}) -> CrewOutput:
        """异步启动方法，用于启动 Crew 执行。"""
        return await asyncio.to_thread(self.kickoff, inputs)

    async def kickoff_for_each_async(self, inputs: List[Dict]) -> List[CrewOutput]:
        crew_copies = [self.copy() for _ in inputs]

        async def run_crew(crew, input_data):
            return await crew.kickoff_async(inputs=input_data)

        tasks = [
            asyncio.create_task(run_crew(crew_copies[i], inputs[i]))
            for i in range(len(inputs))
        ]
        tasks = [
            asyncio.create_task(run_crew(crew_copies[i], inputs[i]))
            for i in range(len(inputs))
        ]

        results = await asyncio.gather(*tasks)

        total_usage_metrics = {
            "total_tokens": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "successful_requests": 0,
        }
        for crew in crew_copies:
            if crew.usage_metrics:
                for key in total_usage_metrics:
                    total_usage_metrics[key] += crew.usage_metrics.get(key, 0)

        self.usage_metrics = total_usage_metrics

        total_usage_metrics = {
            "total_tokens": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "successful_requests": 0,
        }
        for crew in crew_copies:
            if crew.usage_metrics:
                for key in total_usage_metrics:
                    total_usage_metrics[key] += crew.usage_metrics.get(key, 0)

        self.usage_metrics = total_usage_metrics
        self._task_output_handler.reset()
        return results

    def _handle_crew_planning(self):
        """处理 Crew 规划。"""
        self._logger.log("info", "正在规划 Crew 执行")
        # 使用 CrewPlanner 生成每个任务的计划
        result = CrewPlanner(self.tasks)._handle_crew_planning()
        # 将生成的计划添加到对应任务的描述中
        for task, step_plan in zip(self.tasks, result.list_of_plans_per_task):
            task.description += step_plan

    def _store_execution_log(
        self,
        task: Task,
        output: TaskOutput,
        task_index: int,
        was_replayed: bool = False,
    ):
        if self._inputs:
            inputs = self._inputs
        else:
            inputs = {}

        log = {
            "task": task,
            "output": {
                "description": output.description,
                "summary": output.summary,
                "raw": output.raw,
                "pydantic": output.pydantic,
                "json_dict": output.json_dict,
                "output_format": output.output_format,
                "agent": output.agent,
            },
            "task_index": task_index,
            "inputs": inputs,
            "was_replayed": was_replayed,
        }
        self._task_output_handler.update(task_index, log)

    def _run_sequential_process(self) -> CrewOutput:
        """顺序执行任务并返回最终输出。"""
        return self._execute_tasks(self.tasks)

    def _run_hierarchical_process(self) -> CrewOutput:
        """创建并分配管理代理以确保 Crew 完成任务。"""
        self._create_manager_agent()
        return self._execute_tasks(self.tasks, self.manager_agent)

    def _create_manager_agent(self):
        """创建管理者代理。"""
        i18n = I18N(prompt_file=self.prompt_file)
        # 如果已存在管理者代理
        if self.manager_agent is not None:
            # 允许代理进行任务委派
            self.manager_agent.allow_delegation = True
            manager = self.manager_agent
            # 管理者代理不应该拥有工具
            if manager.tools is not None and len(manager.tools) > 0:
                raise Exception("管理者代理不应该拥有工具")
            # 设置管理者代理的工具为代理委派工具
            manager.tools = self.manager_agent.get_delegation_tools(self.agents)
        # 如果不存在管理者代理
        else:
            # 创建一个新的管理者代理
            manager = Agent(
                role=i18n.retrieve("hierarchical_manager_agent", "role"),
                goal=i18n.retrieve("hierarchical_manager_agent", "goal"),
                backstory=i18n.retrieve("hierarchical_manager_agent", "backstory"),
                tools=AgentTools(agents=self.agents).tools(),
                llm=self.manager_llm,
                verbose=self.verbose,
            )
            # 将新创建的管理者代理赋值给 self.manager_agent
            self.manager_agent = manager

    def _execute_tasks(
        self,
        tasks: List[Task],
        manager: Optional[BaseAgent] = None,
        start_index: Optional[int] = 0,
        was_replayed: bool = False,
    ) -> CrewOutput:
        """顺序执行任务并返回最终输出。

        参数：
            tasks (List[Task]): 要执行的任务列表
            manager (Optional[BaseAgent], optional): 用于委托的管理代理。默认为 None。

        返回值：
            CrewOutput:  Crew 的最终输出
        """

        task_outputs: List[TaskOutput] = []
        futures: List[Tuple[Task, Future[TaskOutput], int]] = []
        last_sync_output: Optional[TaskOutput] = None

        for task_index, task in enumerate(tasks):
            if start_index is not None and task_index < start_index:
                if task.output:
                    if task.async_execution:
                        task_outputs.append(task.output)
                    else:
                        task_outputs = [task.output]
                        last_sync_output = task.output
                continue

            agent_to_use = self._get_agent_to_use(task, manager)
            if agent_to_use is None:
                raise ValueError(
                    f"没有可用于任务的代理：{task.description}。确保任务已分配代理或提供了管理代理。"
                )

            self._prepare_agent_tools(task, manager)
            self._log_task_start(task, agent_to_use.role)

            if isinstance(task, ConditionalTask):
                skipped_task_output = self._handle_conditional_task(
                    task, task_outputs, futures, task_index, was_replayed
                )
                if skipped_task_output:
                    continue

            if task.async_execution:
                context = self._get_context(
                    task, [last_sync_output] if last_sync_output else []
                )
                future = task.execute_async(
                    agent=agent_to_use,
                    context=context,
                    tools=agent_to_use.tools,
                )
                futures.append((task, future, task_index))
            else:
                if futures:
                    task_outputs = self._process_async_tasks(futures, was_replayed)
                    futures.clear()

                context = self._get_context(task, task_outputs)
                task_output = task.execute_sync(
                    agent=agent_to_use,
                    context=context,
                    tools=agent_to_use.tools,
                )
                task_outputs = [task_output]
                self._process_task_result(task, task_output)
                self._store_execution_log(task, task_output, task_index, was_replayed)

        if futures:
            task_outputs = self._process_async_tasks(futures, was_replayed)

        return self._create_crew_output(task_outputs)

    def _handle_conditional_task(
        self,
        task: ConditionalTask,
        task_outputs: List[TaskOutput],
        futures: List[Tuple[Task, Future[TaskOutput], int]],
        task_index: int,
        was_replayed: bool,
    ) -> Optional[TaskOutput]:
        """处理条件任务。"""
        # 处理异步任务
        if futures:
            task_outputs = self._process_async_tasks(futures, was_replayed)
            futures.clear()
        # 获取前一个任务的输出
        previous_output = task_outputs[task_index - 1] if task_outputs else None
        # 如果前一个任务的输出不为空且不满足条件任务的执行条件，则跳过该任务
        if previous_output is not None and not task.should_execute(previous_output):
            self._logger.log(
                "debug",
                f"跳过条件任务: {task.description}",
                color="yellow",
            )
            # 获取跳过的任务输出
            skipped_task_output = task.get_skipped_task_output()
            # 如果不是重放，则存储执行日志
            if not was_replayed:
                self._store_execution_log(task, skipped_task_output, task_index)
            # 返回跳过的任务输出
            return skipped_task_output
        # 返回 None
        return None

    def _prepare_agent_tools(self, task: Task, manager: Optional[BaseAgent]):
        """准备代理工具。"""
        # 如果是分层流程
        if self.process == Process.hierarchical:
            # 如果存在管理者代理
            if manager:
                # 更新管理者代理的工具
                self._update_manager_tools(task, manager)
            # 否则抛出异常
            else:
                raise ValueError("分层流程需要管理者代理。")
        # 否则，如果任务的代理允许委派
        elif task.agent and task.agent.allow_delegation:
            # 添加代理委派工具
            self._add_delegation_tools(task)

    def _get_agent_to_use(
        self, task: Task, manager: Optional[BaseAgent]
    ) -> Optional[BaseAgent]:
        if self.process == Process.hierarchical:
            return manager
        return task.agent

    def _add_delegation_tools(self, task: Task):
        agents_for_delegation = [agent for agent in self.agents if agent != task.agent]
        if len(self.agents) > 1 and len(agents_for_delegation) > 0 and task.agent:
            delegation_tools = task.agent.get_delegation_tools(agents_for_delegation)

            # Add tools if they are not already in task.tools
            for new_tool in delegation_tools:
                # Find the index of the tool with the same name
                existing_tool_index = next(
                    (
                        index
                        for index, tool in enumerate(task.tools or [])
                        if tool.name == new_tool.name
                    ),
                    None,
                )
                if not task.tools:
                    task.tools = []

                if existing_tool_index is not None:
                    # Replace the existing tool
                    task.tools[existing_tool_index] = new_tool
                else:
                    # Add the new tool
                    task.tools.append(new_tool)

    def _log_task_start(self, task: Task, role: str = "None"):
        """记录任务开始信息。"""
        color = self._logging_color
        self._logger.log("debug", f"== 工作代理: {role}", color=color)
        self._logger.log("info", f"== 开始任务: {task.description}", color=color)
        # 如果设置了输出日志文件，则将任务开始信息写入文件
        if self.output_log_file:
            self._file_handler.log(agent=role, task=task.description, status="started")

    def _update_manager_tools(self, task: Task, manager: BaseAgent):
        if task.agent:
            manager.tools = task.agent.get_delegation_tools([task.agent])
        else:
            manager.tools = manager.get_delegation_tools(self.agents)

    def _get_context(self, task: Task, task_outputs: List[TaskOutput]):
        context = (
            aggregate_raw_outputs_from_tasks(task.context)
            if task.context
            else aggregate_raw_outputs_from_task_outputs(task_outputs)
        )
        return context

    def _process_task_result(self, task: Task, output: TaskOutput) -> None:
        """处理任务结果。"""
        role = task.agent.role if task.agent is not None else "None"
        self._logger.log("debug", f"== [{role}] 任务输出: {output}\n\n")
        # 如果设置了输出日志文件，则将任务输出写入文件
        if self.output_log_file:
            self._file_handler.log(agent=role, task=output, status="completed")

    def _create_crew_output(self, task_outputs: List[TaskOutput]) -> CrewOutput:
        """创建 Crew 输出。"""
        # 检查任务输出列表长度是否为1
        if len(task_outputs) != 1:
            raise ValueError("出现错误。Kickoff 应该只返回一个任务输出。")
        # 获取最终的任务输出
        final_task_output = task_outputs[0]
        final_string_output = final_task_output.raw
        # 完成执行
        self._finish_execution(final_string_output)
        # 计算使用指标
        token_usage = self.calculate_usage_metrics()
        # 返回 Crew 输出
        return CrewOutput(
            raw=final_task_output.raw,
            pydantic=final_task_output.pydantic,
            json_dict=final_task_output.json_dict,
            tasks_output=[task.output for task in self.tasks if task.output],
            token_usage=token_usage,
        )

    def _process_async_tasks(
        self,
        futures: List[Tuple[Task, Future[TaskOutput], int]],
        was_replayed: bool = False,
    ) -> List[TaskOutput]:
        task_outputs: List[TaskOutput] = []
        for future_task, future, task_index in futures:
            task_output = future.result()
            task_outputs.append(task_output)
            self._process_task_result(future_task, task_output)
            self._store_execution_log(
                future_task, task_output, task_index, was_replayed
            )
        return task_outputs

    def _find_task_index(
        self, task_id: str, stored_outputs: List[Any]
    ) -> Optional[int]:
        return next(
            (
                index
                for (index, d) in enumerate(stored_outputs)
                if d["task_id"] == str(task_id)
            ),
            None,
        )

    def replay(
        self, task_id: str, inputs: Optional[Dict[str, Any]] = None
    ) -> CrewOutput:
        """重放从指定任务 ID 开始的 Crew 执行。"""
        # 加载已存储的任务输出
        stored_outputs = self._task_output_handler.load()
        # 如果没有存储的任务输出，则抛出异常
        if not stored_outputs:
            raise ValueError(f"在 Crew 的任务中找不到 ID 为 {task_id} 的任务。")
        # 查找指定任务 ID 的任务索引
        start_index = self._find_task_index(task_id, stored_outputs)
        # 如果找不到指定任务 ID 的任务，则抛出异常
        if start_index is None:
            raise ValueError(f"在 Crew 的任务中找不到 ID 为 {task_id} 的任务。")
        # 获取重放输入
        replay_inputs = (
            inputs if inputs is not None else stored_outputs[start_index]["inputs"]
        )
        self._inputs = replay_inputs
        # 如果存在重放输入，则进行插值
        if replay_inputs:
            self._interpolate_inputs(replay_inputs)
        # 如果是分层流程，则创建管理者代理
        if self.process == Process.hierarchical:
            self._create_manager_agent()
        # 加载之前任务的输出作为上下文
        for i in range(start_index):
            stored_output = stored_outputs[i]["output"]
            task_output = TaskOutput(
                description=stored_output["description"],
                agent=stored_output["agent"],
                raw=stored_output["raw"],
                pydantic=stored_output["pydantic"],
                json_dict=stored_output["json_dict"],
                output_format=stored_output["output_format"],
            )
            self.tasks[i].output = task_output
        # 设置日志颜色为蓝色
        self._logging_color = "bold_blue"
        # 从指定索引开始执行任务
        result = self._execute_tasks(self.tasks, self.manager_agent, start_index, True)
        # 返回执行结果
        return result

    def copy(self):
        """创建 Crew 的深拷贝。"""

        exclude = {
            "id",
            "_rpm_controller",
            "_logger",
            "_execution_span",
            "_file_handler",
            "_cache_handler",
            "_short_term_memory",
            "_long_term_memory",
            "_entity_memory",
            "_telemetry",
            "agents",
            "tasks",
        }

        cloned_agents = [agent.copy() for agent in self.agents]
        cloned_tasks = [task.copy(cloned_agents) for task in self.tasks]

        copied_data = self.model_dump(exclude=exclude)
        copied_data = {k: v for k, v in copied_data.items() if v is not None}

        copied_data.pop("agents", None)
        copied_data.pop("tasks", None)

        copied_crew = Crew(**copied_data, agents=cloned_agents, tasks=cloned_tasks)

        return copied_crew

    def _set_tasks_callbacks(self) -> None:
        """使用 task_callback 为每个任务设置回调"""
        for task in self.tasks:
            if not task.callback:
                task.callback = self.task_callback

    def _interpolate_inputs(self, inputs: Dict[str, Any]) -> None:
        """在任务和代理中插值输入。"""
        [
            task.interpolate_inputs(
                # type: ignore # "interpolate_inputs" of "Task" does not return a value (it only ever returns None)
                inputs
            )
            for task in self.tasks
        ]
        # type: ignore # "interpolate_inputs" of "Agent" does not return a value (it only ever returns None)
        for agent in self.agents:
            agent.interpolate_inputs(inputs)

    def _finish_execution(self, final_string_output: str) -> None:
        """完成 Crew 执行。"""
        # 如果设置了最大请求速率，则停止请求速率计数器
        if self.max_rpm:
            self._rpm_controller.stop_rpm_counter()
        # 如果使用了 agentops，则结束 agentops 会话
        if agentops:
            agentops.end_session(
                end_state="Success",
                end_state_reason="执行完毕",
            )
        # 发送遥测数据，指示 Crew 执行结束
        self._telemetry.end_crew(self, final_string_output)

    def calculate_usage_metrics(self) -> Dict[str, int]:
        """计算并返回使用情况指标。"""
        total_usage_metrics = {
            "total_tokens": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "successful_requests": 0,
        }

        for agent in self.agents:
            if hasattr(agent, "_token_process"):
                token_sum = agent._token_process.get_summary()
                for key in total_usage_metrics:
                    total_usage_metrics[key] += token_sum.get(key, 0)

        if self.manager_agent and hasattr(self.manager_agent, "_token_process"):
            token_sum = self.manager_agent._token_process.get_summary()
            for key in total_usage_metrics:
                total_usage_metrics[key] += token_sum.get(key, 0)

        return total_usage_metrics

    def __repr__(self):
        """返回 Crew 对象的字符串表示形式。"""
        return f"Crew(id={self.id}, process={self.process}, number_of_agents={len(self.agents)}, number_of_tasks={len(self.tasks)})"
