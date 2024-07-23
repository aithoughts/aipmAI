import os
from inspect import signature
from typing import Any, List, Optional, Tuple

from langchain.agents.agent import RunnableAgent
from langchain.agents.tools import BaseTool
from langchain.agents.tools import tool as LangChainTool
from langchain_core.agents import AgentAction
from langchain_core.callbacks import BaseCallbackHandler
from langchain_openai import ChatOpenAI
from pydantic import Field, InstanceOf, PrivateAttr, model_validator

from crewai.agents import CacheHandler, CrewAgentExecutor, CrewAgentParser
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.memory.contextual.contextual_memory import ContextualMemory
from crewai.tools.agent_tools import AgentTools
from crewai.utilities import Converter, Prompts
from crewai.utilities.constants import TRAINED_AGENTS_DATA_FILE, TRAINING_DATA_FILE
from crewai.utilities.token_counter_callback import TokenCalcHandler
from crewai.utilities.training_handler import CrewTrainingHandler

agentops = None
try:
    import agentops  # type: ignore # 名字 "agentops" 已在第 21 行定义
    from agentops import track_agent
except ImportError:

    def track_agent():
        def noop(f):
            return f

        return noop


@track_agent()
class Agent(BaseAgent):
    """表示系统中的代理。

    每个代理都有一个角色、一个目标、一个背景故事和一个可选的语言模型 (llm)。
    代理还可以拥有记忆，可以在详细模式下运行，并且可以将任务委派给其他代理。

    属性：
            agent_executor: CrewAgentExecutor 类的一个实例。
            role: 代理的角色。
            goal: 代理的目标。
            backstory: 代理的背景故事。
            config: 代理配置的字典表示形式。
            llm: 将运行代理的语言模型。
            function_calling_llm: 将为此代理处理工具调用的语言模型，它会覆盖 crew function_calling_llm。
            max_iter: 代理执行任务的最大迭代次数。
            memory: 代理是否应该有记忆。
            max_rpm: 要遵守的代理执行每分钟最大请求数。
            verbose: 代理执行是否应处于详细模式。
            allow_delegation: 是否允许代理将任务委派给其他代理。
            tools: 代理可用的工具
            step_callback: 在代理执行的每个步骤之后执行的回调。
            callbacks: langchain 库中的一系列回调函数，在代理的执行过程中触发
            allow_code_execution: 为代理启用代码执行。
            max_retry_limit: 当发生错误时，代理执行任务的最大重试次数。
    """

    _times_executed: int = PrivateAttr(default=0)
    max_execution_time: Optional[int] = Field(
        default=None,
        description="代理执行任务的最长执行时间",
    )
    agent_ops_agent_name: str = None  # type: ignore #  赋值时类型不兼容 (表达式的类型是 "None"，变量的类型是 "str")
    agent_ops_agent_id: str = None  # type: ignore #  赋值时类型不兼容 (表达式的类型是 "None"，变量的类型是 "str")
    cache_handler: InstanceOf[CacheHandler] = Field(
        default=None, description="CacheHandler 类的一个实例。"
    )
    step_callback: Optional[Any] = Field(
        default=None,
        description="在代理执行的每个步骤之后执行的回调。",
    )
    llm: Any = Field(
        default_factory=lambda: ChatOpenAI(
            model=os.environ.get("OPENAI_MODEL_NAME", "gpt-4o")
        ),
        description="将运行代理的语言模型。",
    )
    function_calling_llm: Optional[Any] = Field(
        description="将运行代理的语言模型。", default=None
    )
    callbacks: Optional[List[InstanceOf[BaseCallbackHandler]]] = Field(
        default=None, description="要执行的回调"
    )
    system_template: Optional[str] = Field(
        default=None, description="代理的系统格式。"
    )
    prompt_template: Optional[str] = Field(
        default=None, description="代理的提示格式。"
    )
    response_template: Optional[str] = Field(
        default=None, description="代理的响应格式。"
    )
    tools_results: Optional[List[Any]] = Field(
        default=[], description="代理使用的工具的结果。"
    )
    allow_code_execution: Optional[bool] = Field(
        default=False, description="为代理启用代码执行。"
    )
    max_retry_limit: int = Field(
        default=2,
        description="当发生错误时，代理执行任务的最大重试次数。",
    )

    def __init__(__pydantic_self__, **data):
        config = data.pop("config", {})
        super().__init__(**config, **data)
        __pydantic_self__.agent_ops_agent_name = __pydantic_self__.role

    @model_validator(mode="after")
    def set_agent_executor(self) -> "Agent":
        """确保设置了代理执行器和标记进程。"""
        if hasattr(self.llm, "model_name"):
            token_handler = TokenCalcHandler(self.llm.model_name, self._token_process)

            # 确保 self.llm.callbacks 是一个列表
            if not isinstance(self.llm.callbacks, list):
                self.llm.callbacks = []

            # 检查列表中是否已存在 TokenCalcHandler 的实例
            if not any(
                isinstance(handler, TokenCalcHandler) for handler in self.llm.callbacks
            ):
                self.llm.callbacks.append(token_handler)

            if agentops and not any(
                isinstance(handler, agentops.LangchainCallbackHandler)
                for handler in self.llm.callbacks
            ):
                agentops.stop_instrumenting()
                self.llm.callbacks.append(agentops.LangchainCallbackHandler())

        if not self.agent_executor:
            if not self.cache_handler:
                self.cache_handler = CacheHandler()
            self.set_cache_handler(self.cache_handler)
        return self

    def execute_task(
        self,
        task: Any,
        context: Optional[str] = None,
        tools: Optional[List[Any]] = None,
    ) -> str:
        """使用代理执行任务。

        参数：
            task: 要执行的任务。
            context: 在其中执行任务的上下文。
            tools: 用于任务的工具。

        返回值：
            代理的输出
        """
        if self.tools_handler:
            self.tools_handler.last_used_tool = {}  # type: ignore # 赋值时类型不兼容 (表达式的类型是 "dict[Never, Never]", 变量的类型是 "ToolCalling")

        task_prompt = task.prompt()

        if context:
            task_prompt = self.i18n.slice("task_with_context").format(
                task=task_prompt, context=context
            )

        if self.crew and self.crew.memory:
            contextual_memory = ContextualMemory(
                self.crew._short_term_memory,
                self.crew._long_term_memory,
                self.crew._entity_memory,
            )
            memory = contextual_memory.build_context_for_task(task, context)
            if memory.strip() != "":
                task_prompt += self.i18n.slice("memory").format(memory=memory)

        tools = tools or self.tools or []
        parsed_tools = self._parse_tools(tools)
        self.create_agent_executor(tools=tools)
        self.agent_executor.tools = parsed_tools
        self.agent_executor.task = task

        self.agent_executor.tools_description = (
            self._render_text_description_and_args(parsed_tools)
        )
        self.agent_executor.tools_names = self.__tools_names(parsed_tools)

        if self.crew and self.crew._train:
            task_prompt = self._training_handler(task_prompt=task_prompt)
        else:
            task_prompt = self._use_trained_data(task_prompt=task_prompt)

        try:
            result = self.agent_executor.invoke(
                {
                    "input": task_prompt,
                    "tool_names": self.agent_executor.tools_names,
                    "tools": self.agent_executor.tools_description,
                }
            )["output"]
        except Exception as e:
            self._times_executed += 1
            if self._times_executed > self.max_retry_limit:
                raise e
            result = self.execute_task(task, context, tools)

        if self.max_rpm:
            self._rpm_controller.stop_rpm_counter()

        # 如果 self.tools_results 中有任何工具的 result_as_answer
        # 设置为 True，则返回最后一个 result_as_answer
        # 设置为 True 的工具的结果
        for tool_result in self.tools_results:  # type: ignore # "list[Any] | None" 中的 "None" 元素没有 "__iter__" 属性 (不可迭代)
            if tool_result.get("result_as_answer", False):
                result = tool_result["result"]

        return result

    def format_log_to_str(
        self,
        intermediate_steps: List[Tuple[AgentAction, str]],  # 中间步骤列表，每个元素是一个元组，包含 AgentAction 和观察结果
        observation_prefix: str = "Observation: ",  # 观察结果的前缀，默认为 "Observation: "
        llm_prefix: str = "",  # LLM 输出的前缀，默认为空字符串
    ) -> str:
        """构造允许代理继续其思考过程的草稿板"""
        thoughts = ""  # 初始化一个空字符串，用于存储拼接后的日志信息
        for action, observation in intermediate_steps:  # 遍历中间步骤列表
            thoughts += action.log  # 将动作日志添加到 thoughts 字符串中
            thoughts += f"\n{observation_prefix}{observation}\n{llm_prefix}"  # 将观察结果和前缀添加到 thoughts 字符串中
        return thoughts  # 返回拼接后的日志字符串

    def create_agent_executor(self, tools=None) -> None:
        """为代理创建代理执行器。

        返回值：
            CrewAgentExecutor 类的一个实例。
        """
        tools = tools or self.tools or []

        agent_args = {
            "input": lambda x: x["input"],
            "tools": lambda x: x["tools"],
            "tool_names": lambda x: x["tool_names"],
            "agent_scratchpad": lambda x: self.format_log_to_str(
                x["intermediate_steps"]
            ),
        }

        executor_args = {
            "llm": self.llm,
            "i18n": self.i18n,
            "crew": self.crew,
            "crew_agent": self,
            "tools": self._parse_tools(tools),
            "verbose": self.verbose,
            "original_tools": tools,
            "handle_parsing_errors": True,
            "max_iterations": self.max_iter,
            "max_execution_time": self.max_execution_time,
            "step_callback": self.step_callback,
            "tools_handler": self.tools_handler,
            "function_calling_llm": self.function_calling_llm,
            "callbacks": self.callbacks,
        }

        if self._rpm_controller:
            executor_args["request_within_rpm_limit"] = (
                self._rpm_controller.check_or_wait
            )

        prompt = Prompts(
            i18n=self.i18n,
            tools=tools,
            system_template=self.system_template,
            prompt_template=self.prompt_template,
            response_template=self.response_template,
        ).task_execution()

        execution_prompt = prompt.partial(
            goal=self.goal,
            role=self.role,
            backstory=self.backstory,
        )

        stop_words = [self.i18n.slice("observation")]

        if self.response_template:
            stop_words.append(
                self.response_template.split("{{ .Response }}")[1].strip()
            )

        bind = self.llm.bind(stop=stop_words)

        inner_agent = agent_args | execution_prompt | bind | CrewAgentParser(agent=self)
        self.agent_executor = CrewAgentExecutor(
            agent=RunnableAgent(runnable=inner_agent), **executor_args
        )

    def get_delegation_tools(self, agents: List[BaseAgent]):
        agent_tools = AgentTools(agents=agents)
        tools = agent_tools.tools()
        return tools

    def get_code_execution_tools(self):
        try:
            from crewai_tools import CodeInterpreterTool

            return [CodeInterpreterTool()]
        except ModuleNotFoundError:
            self._logger.log(
                "info", "编码工具不可用。安装 crewai_tools。 "
            )

    def get_output_converter(self, llm, text, model, instructions):
        return Converter(llm=llm, text=text, model=model, instructions=instructions)

    def _parse_tools(self, tools: List[Any]) -> List[LangChainTool]:  # type: ignore # Function "langchain_core.tools.tool" is not valid as a type
        """解析要用于任务的工具。"""
        tools_list = []
        try:
            # 尝试从 crewai_tools import BaseTool as CrewAITool
            from crewai_tools import BaseTool as CrewAITool

            for tool in tools:
                if isinstance(tool, CrewAITool):
                    tools_list.append(tool.to_langchain())
                else:
                    tools_list.append(tool)
        except ModuleNotFoundError:
            tools_list = []
            for tool in tools:
                tools_list.append(tool)

        return tools_list

    def _training_handler(self, task_prompt: str) -> str:
        """处理代理任务提示的训练数据，以改进训练时的输出。"""
        if data := CrewTrainingHandler(TRAINING_DATA_FILE).load():
            agent_id = str(self.id)

            if data.get(agent_id):
                human_feedbacks = [
                    i["human_feedback"] for i in data.get(agent_id, {}).values()
                ]
                task_prompt += "您必须遵循以下反馈：\n " + "\n - ".join(
                    human_feedbacks
                )

        return task_prompt

    def _use_trained_data(self, task_prompt: str) -> str:
        """使用代理任务提示的训练数据来改进输出。"""
        if data := CrewTrainingHandler(TRAINED_AGENTS_DATA_FILE).load():
            if trained_data_output := data.get(self.role):
                task_prompt += "您必须遵循以下反馈：\n " + "\n - ".join(
                    trained_data_output["suggestions"]
                )
        return task_prompt

    def _render_text_description(self, tools: List[BaseTool]) -> str:
        """以纯文本形式呈现工具名称和描述。

        输出格式如下：

        .. code-block:: markdown

            search: 此工具用于搜索
            calculator: 此工具用于数学运算
        """
        description = "\n".join(
            [
                f"工具名称：{tool.name}\n工具描述：\n{tool.description}"
                for tool in tools
            ]
        )

        return description

    def _render_text_description_and_args(self, tools: List[BaseTool]) -> str:
        """以纯文本形式呈现工具名称、描述和参数。

        输出格式如下：

        .. code-block:: markdown

            search: 此工具用于搜索，参数：{"query": {"type": "string"}}
            calculator: 此工具用于数学运算，\
    参数：{"expression": {"type": "string"}}
        """
        tool_strings = []
        for tool in tools:
            args_schema = str(tool.args)
            if hasattr(tool, "func") and tool.func:
                sig = signature(tool.func)
                description = (
                    f"工具名称：{tool.name}{sig}\n工具描述：{tool.description}"
                )
            else:
                description = (
                    f"工具名称：{tool.name}\n工具描述：{tool.description}"
                )
            tool_strings.append(f"{description}\n工具参数：{args_schema}")

        return "\n".join(tool_strings)

    @staticmethod
    def __tools_names(tools) -> str:
        return ", ".join([t.name for t in tools])

    def __repr__(self):
        return f"Agent(role={self.role}, goal={self.goal}, backstory={self.backstory})"
