import uuid
from abc import ABC, abstractmethod
from copy import copy as shallow_copy
from hashlib import md5
from typing import Any, Dict, List, Optional, TypeVar

from pydantic import (
    UUID4,
    BaseModel,
    ConfigDict,
    Field,
    InstanceOf,
    PrivateAttr,
    field_validator,
    model_validator,
)
from pydantic_core import PydanticCustomError

from crewai.agents.agent_builder.utilities.base_token_process import TokenProcess
from crewai.agents.cache.cache_handler import CacheHandler
from crewai.agents.tools_handler import ToolsHandler
from crewai.utilities import I18N, Logger, RPMController

T = TypeVar("T", bound="BaseAgent")


class BaseAgent(ABC, BaseModel):
    """与 CrewAI 兼容的所有第三方代理的抽象基类。

    属性：
        id (UUID4): 代理的唯一标识符。
        role (str): 代理的角色。
        goal (str): 代理的目标。
        backstory (str): 代理的背景故事。
        cache (bool): 代理是否应使用缓存来进行工具使用。
        config (Optional[Dict[str, Any]]): 代理的配置。
        verbose (bool): 代理执行的详细模式。
        max_rpm (Optional[int]): 代理执行每分钟最大请求数。
        allow_delegation (bool): 允许将任务委派给代理。
        tools (Optional[List[Any]]): 代理可用的工具。
        max_iter (Optional[int]): 代理执行任务的最大迭代次数。
        agent_executor (InstanceOf): CrewAgentExecutor 类的一个实例。
        llm (Any): 将运行代理的语言模型。
        crew (Any): 代理所属的团队。
        i18n (I18N): 国际化设置。
        cache_handler (InstanceOf[CacheHandler]): CacheHandler 类的一个实例。
        tools_handler (InstanceOf[ToolsHandler]): ToolsHandler 类的一个实例。


    方法：
        execute_task(task: Any, context: Optional[str] = None, tools: Optional[List[Any]] = None) -> str:
            执行任务的抽象方法。
        create_agent_executor(tools=None) -> None:
            创建代理执行器的抽象方法。
        _parse_tools(tools: List[Any]) -> List[Any]:
            解析工具的抽象方法。
        get_delegation_tools(agents: List["BaseAgent"]):
            设置代理任务工具的抽象方法，用于处理委派和向团队中其他代理询问问题。
        get_output_converter(llm, model, instructions):
            获取代理用于创建 json/pydantic 输出的转换器类的抽象方法。
        interpolate_inputs(inputs: Dict[str, Any]) -> None:
            将输入插入代理描述和背景故事。
        set_cache_handler(cache_handler: CacheHandler) -> None:
            设置代理的缓存处理程序。
        increment_formatting_errors() -> None:
            增加格式错误。
        copy() -> "BaseAgent":
            创建代理的副本。
        set_rpm_controller(rpm_controller: RPMController) -> None:
            设置代理的 rpm 控制器。
        set_private_attrs() -> "BaseAgent":
            设置私有属性。
    """

    __hash__ = object.__hash__  # type: ignore
    _logger: Logger = PrivateAttr()
    _rpm_controller: RPMController = PrivateAttr(default=None)
    _request_within_rpm_limit: Any = PrivateAttr(default=None)
    formatting_errors: int = 0
    model_config = ConfigDict(arbitrary_types_allowed=True)
    id: UUID4 = Field(default_factory=uuid.uuid4, frozen=True)
    role: str = Field(description="代理的角色")
    goal: str = Field(description="代理的目标")
    backstory: str = Field(description="代理的背景故事")
    cache: bool = Field(
        default=True, description="代理是否应使用缓存来进行工具使用。"
    )
    config: Optional[Dict[str, Any]] = Field(
        description="代理的配置", default=None
    )
    verbose: bool = Field(
        default=False, description="代理执行的详细模式"
    )
    max_rpm: Optional[int] = Field(
        default=None,
        description="要遵守的代理执行每分钟最大请求数。",
    )
    allow_delegation: bool = Field(
        default=True, description="允许将任务委派给代理"
    )
    tools: Optional[List[Any]] = Field(
        default_factory=list, description="代理可用的工具"
    )
    max_iter: Optional[int] = Field(
        default=25, description="代理执行任务的最大迭代次数"
    )
    agent_executor: InstanceOf = Field(
        default=None, description="CrewAgentExecutor 类的一个实例。"
    )
    llm: Any = Field(
        default=None, description="将运行代理的语言模型。"
    )
    crew: Any = Field(default=None, description="代理所属的团队。")
    i18n: I18N = Field(default=I18N(), description="国际化设置。")
    cache_handler: InstanceOf[CacheHandler] = Field(
        default=None, description="CacheHandler 类的一个实例。"
    )
    tools_handler: InstanceOf[ToolsHandler] = Field(
        default=None, description="ToolsHandler 类的一个实例。"
    )

    _original_role: str | None = None
    _original_goal: str | None = None
    _original_backstory: str | None = None
    _token_process: TokenProcess = TokenProcess()

    def __init__(__pydantic_self__, **data):
        config = data.pop("config", {})
        super().__init__(**config, **data)

    @model_validator(mode="after")
    def set_config_attributes(self):
        if self.config:
            for key, value in self.config.items():
                setattr(self, key, value)
        return self

    @field_validator("id", mode="before")
    @classmethod
    def _deny_user_set_id(cls, v: Optional[UUID4]) -> None:
        if v:
            raise PydanticCustomError(
                "may_not_set_field", "用户不得设置此字段。", {}
            )

    @model_validator(mode="after")
    def set_attributes_based_on_config(self) -> "BaseAgent":
        """根据代理配置设置属性。"""
        if self.config:
            for key, value in self.config.items():
                setattr(self, key, value)
        return self

    @model_validator(mode="after")
    def set_private_attrs(self):
        """设置私有属性。"""
        self._logger = Logger(self.verbose)
        if self.max_rpm and not self._rpm_controller:
            self._rpm_controller = RPMController(
                max_rpm=self.max_rpm, logger=self._logger
            )
        if not self._token_process:
            self._token_process = TokenProcess()
        return self

    @property
    def key(self):
        source = [self.role, self.goal, self.backstory]
        return md5("|".join(source).encode()).hexdigest()

    @abstractmethod
    def execute_task(
        self,
        task: Any,
        context: Optional[str] = None,
        tools: Optional[List[Any]] = None,
    ) -> str:
        pass

    @abstractmethod
    def create_agent_executor(self, tools=None) -> None:
        pass

    @abstractmethod
    def _parse_tools(self, tools: List[Any]) -> List[Any]:
        pass

    @abstractmethod
    def get_delegation_tools(self, agents: List["BaseAgent"]) -> List[Any]:
        """设置初始化 BaseAgenTools 类的任务工具。"""
        pass

    @abstractmethod
    def get_output_converter(
        self, llm: Any, text: str, model: type[BaseModel] | None, instructions: str
    ):
        """获取代理用于创建 json/pydantic 输出的转换器类。"""
        pass

    def copy(self: T) -> T:  # type: ignore # Signature of "copy" incompatible with supertype "BaseModel"
        """创建代理的深层副本。"""
        exclude = {
            "id",
            "_logger",
            "_rpm_controller",
            "_request_within_rpm_limit",
            "_token_process",
            "agent_executor",
            "tools",
            "tools_handler",
            "cache_handler",
            "llm",
        }

        # 复制 llm 并清除回调
        existing_llm = shallow_copy(self.llm)
        existing_llm.callbacks = []
        copied_data = self.model_dump(exclude=exclude)
        copied_data = {k: v for k, v in copied_data.items() if v is not None}

        copied_agent = type(self)(**copied_data, llm=existing_llm, tools=self.tools)

        return copied_agent

    def interpolate_inputs(self, inputs: Dict[str, Any]) -> None:
        """将输入插入代理描述和背景故事。"""
        if self._original_role is None:
            self._original_role = self.role
        if self._original_goal is None:
            self._original_goal = self.goal
        if self._original_backstory is None:
            self._original_backstory = self.backstory

        if inputs:
            self.role = self._original_role.format(**inputs)
            self.goal = self._original_goal.format(**inputs)
            self.backstory = self._original_backstory.format(**inputs)

    def set_cache_handler(self, cache_handler: CacheHandler) -> None:
        """设置代理的缓存处理程序。

        参数：
            cache_handler: CacheHandler 类的一个实例。
        """
        self.tools_handler = ToolsHandler()
        if self.cache:
            self.cache_handler = cache_handler
            self.tools_handler.cache = cache_handler
        self.create_agent_executor()

    def increment_formatting_errors(self) -> None:
        self.formatting_errors += 1

    def set_rpm_controller(self, rpm_controller: RPMController) -> None:
        """设置代理的 rpm 控制器。

        参数：
            rpm_controller: RPMController 类的一个实例。
        """
        if not self._rpm_controller:
            self._rpm_controller = rpm_controller
            self.create_agent_executor()
