import json
import os
import re
import threading
import uuid
from concurrent.futures import Future
from copy import copy
from hashlib import md5
from typing import Any, Dict, List, Optional, Tuple, Type, Union

from langchain_openai import ChatOpenAI
from opentelemetry.trace import Span
from pydantic import UUID4, BaseModel, Field, field_validator, model_validator
from pydantic_core import PydanticCustomError

from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.tasks.output_format import OutputFormat
from crewai.tasks.task_output import TaskOutput
from crewai.telemetry.telemetry import Telemetry
from crewai.utilities.converter import Converter, ConverterError
from crewai.utilities.i18n import I18N
from crewai.utilities.printer import Printer
from crewai.utilities.pydantic_schema_parser import PydanticSchemaParser


class Task(BaseModel):
    """表示要执行的任务的类。

    每个任务都必须有一个描述、一个预期的输出和一个负责执行的代理。

    属性：
        agent: 负责任务执行的代理。表示执行任务的实体。
        async_execution: 布尔标志，指示是否异步执行任务。
        callback: 任务完成后执行的函数/对象，用于执行其他操作。
        config: 包含特定于任务的配置参数的字典。
        context: 提供任务上下文或输入数据的任务实例列表。
        description: 详细说明任务目的和执行的描述性文本。
        expected_output: 对预期任务结果的清晰定义。
        output_file: 用于存储任务输出的文件路径。
        output_json: 用于构建 JSON 输出的 Pydantic 模型。
        output_pydantic: 用于任务输出的 Pydantic 模型。
        tools: 限制用于任务执行的工具/资源列表。
    """

    class Config:
        arbitrary_types_allowed = True

    __hash__ = object.__hash__  # type: ignore
    used_tools: int = 0
    tools_errors: int = 0
    delegations: int = 0
    i18n: I18N = I18N()
    prompt_context: Optional[str] = None
    description: str = Field(description="实际任务的描述。")
    expected_output: str = Field(
        description="对任务预期输出的清晰定义。"
    )
    config: Optional[Dict[str, Any]] = Field(
        description="代理的配置",
        default=None,
    )
    callback: Optional[Any] = Field(
        description="任务完成后要执行的回调。", default=None
    )
    agent: Optional[BaseAgent] = Field(
        description="负责执行任务的代理。", default=None
    )
    context: Optional[List["Task"]] = Field(
        description="其他任务，其输出将用作此任务的上下文。",
        default=None,
    )
    async_execution: Optional[bool] = Field(
        description="任务是否应该异步执行。",
        default=False,
    )
    output_json: Optional[Type[BaseModel]] = Field(
        description="用于创建 JSON 输出的 Pydantic 模型。",
        default=None,
    )
    output_pydantic: Optional[Type[BaseModel]] = Field(
        description="用于创建 Pydantic 输出的 Pydantic 模型。",
        default=None,
    )
    output_file: Optional[str] = Field(
        description="用于创建文件输出的文件路径。",
        default=None,
    )
    output: Optional[TaskOutput] = Field(
        description="任务输出，执行后的最终结果", default=None
    )
    tools: Optional[List[Any]] = Field(
        default_factory=list,
        description="代理被限制用于此任务的工具。",
    )
    id: UUID4 = Field(
        default_factory=uuid.uuid4,
        frozen=True,
        description="对象的唯一标识符，不由用户设置。",
    )
    human_input: Optional[bool] = Field(
        description="任务是否应该由人工审核代理的最终答案",
        default=False,
    )
    converter_cls: Optional[Type[Converter]] = Field(
        description="用于导出结构化输出的转换器类",
        default=None,
    )

    # _telemetry: Telemetry
    # _execution_span: Span | None = None
    _original_description: str | None = None
    _original_expected_output: str | None = None
    _thread: threading.Thread | None = None

    def __init__(__pydantic_self__, **data):
        config = data.pop("config", {})
        super().__init__(**config, **data)

    @field_validator("id", mode="before")
    @classmethod
    def _deny_user_set_id(cls, v: Optional[UUID4]) -> None:
        if v:
            raise PydanticCustomError(
                "may_not_set_field", "此字段不能由用户设置。", {}
            )

    @field_validator("output_file")
    @classmethod
    def output_file_validattion(cls, value: str) -> str:
        """通过删除路径开头的 / 来验证输出文件路径。"""
        if value.startswith("/"):
            return value[1:]
        return value

    @model_validator(mode="after")
    def set_private_attrs(self) -> "Task":
        """设置私有属性。"""
        self._telemetry = Telemetry()
        return self

    @model_validator(mode="after")
    def set_attributes_based_on_config(self) -> "Task":
        """根据代理配置设置属性。"""
        if self.config:
            for key, value in self.config.items():
                setattr(self, key, value)
        return self

    @model_validator(mode="after")
    def check_tools(self):
        """检查是否设置了工具。"""
        if not self.tools and self.agent and self.agent.tools:
            self.tools.extend(self.agent.tools)
        return self

    @model_validator(mode="after")
    def check_output(self):
        """检查是否设置了输出类型。"""
        output_types = [self.output_json, self.output_pydantic]
        if len([type for type in output_types if type]) > 1:
            raise PydanticCustomError(
                "output_type",
                "只能设置一种输出类型，output_pydantic 或 output_json。",
                {},
            )
        return self

    def execute_sync(
        self,
        agent: Optional[BaseAgent] = None,
        context: Optional[str] = None,
        tools: Optional[List[Any]] = None,
    ) -> TaskOutput:
        """同步执行任务。"""
        return self._execute_core(agent, context, tools)

    @property
    def key(self) -> str:
        description = self._original_description or self.description
        expected_output = self._original_expected_output or self.expected_output
        source = [description, expected_output]

        return md5("|".join(source).encode()).hexdigest()

    def execute_async(
        self,
        agent: BaseAgent | None = None,
        context: Optional[str] = None,
        tools: Optional[List[Any]] = None,
    ) -> Future[TaskOutput]:
        """异步执行任务。"""
        future: Future[TaskOutput] = Future()
        threading.Thread(
            target=self._execute_task_async, args=(agent, context, tools, future)
        ).start()
        return future

    def _execute_task_async(
        self,
        agent: Optional[BaseAgent],
        context: Optional[str],
        tools: Optional[List[Any]],
        future: Future[TaskOutput],
    ) -> None:
        """在处理上下文的情况下异步执行任务。"""
        result = self._execute_core(agent, context, tools)
        future.set_result(result)

    def _execute_core(
        self,
        agent: Optional[BaseAgent],
        context: Optional[str],
        tools: Optional[List[Any]],
    ) -> TaskOutput:
        """运行任务的核心执行逻辑。"""
        agent = agent or self.agent
        self.agent = agent
        if not agent:
            raise Exception(
                f"任务 '{self.description}' 没有分配代理，因此它不能直接执行，应该在 Crew 中使用支持该任务的特定流程执行，例如分层流程。"
            )

        # self._execution_span = self._telemetry.task_started(crew=agent.crew, task=self)

        self.prompt_context = context
        tools = tools or self.tools or []

        result = agent.execute_task(
            task=self,
            context=context,
            tools=tools,
        )

        pydantic_output, json_output = self._export_output(result)

        task_output = TaskOutput(
            description=self.description,
            raw=result,
            pydantic=pydantic_output,
            json_dict=json_output,
            agent=agent.role,
            output_format=self._get_output_format(),
        )
        self.output = task_output

        if self.callback:
            self.callback(self.output)

        # if self._execution_span:
        #     self._telemetry.task_ended(self._execution_span, self, agent.crew)
        #     self._execution_span = None

        if self.output_file:
            content = (
                json_output
                if json_output
                else pydantic_output.model_dump_json()
                if pydantic_output
                else result
            )
            self._save_file(content)

        return task_output

    def prompt(self) -> str:
        """提示任务。

        返回：
            任务提示。
        """
        tasks_slices = [self.description]

        output = self.i18n.slice("expected_output").format(
            expected_output=self.expected_output
        )
        tasks_slices = [self.description, output]
        return "\n".join(tasks_slices)

    def interpolate_inputs(self, inputs: Dict[str, Any]) -> None:
        """将输入插入到任务描述和预期输出中。"""
        if self._original_description is None:
            self._original_description = self.description
        if self._original_expected_output is None:
            self._original_expected_output = self.expected_output

        if inputs:
            self.description = self._original_description.format(**inputs)
            self.expected_output = self._original_expected_output.format(**inputs)

    def increment_tools_errors(self) -> None:
        """增加工具错误计数器。"""
        self.tools_errors += 1

    def increment_delegations(self) -> None:
        """增加委托计数器。"""
        self.delegations += 1

    def copy(self, agents: List["BaseAgent"]) -> "Task":
        """创建任务的深层副本。"""
        exclude = {
            "id",
            "agent",
            "context",
            "tools",
        }

        copied_data = self.model_dump(exclude=exclude)
        copied_data = {k: v for k, v in copied_data.items() if v is not None}

        cloned_context = (
            [task.copy(agents) for task in self.context] if self.context else None
        )

        def get_agent_by_role(role: str) -> Union["BaseAgent", None]:
            return next((agent for agent in agents if agent.role == role), None)

        cloned_agent = get_agent_by_role(self.agent.role) if self.agent else None
        cloned_tools = copy(self.tools) if self.tools else []

        copied_task = Task(
            **copied_data,
            context=cloned_context,
            agent=cloned_agent,
            tools=cloned_tools,
        )

        return copied_task

    def _create_converter(self, *args, **kwargs) -> Converter:
        """创建一个转换器实例。"""
        if self.agent and not self.converter_cls:
            converter = self.agent.get_output_converter(*args, **kwargs)
        elif self.converter_cls:
            converter = self.converter_cls(*args, **kwargs)

        if not converter:
            raise Exception("未找到或设置输出转换器。")

        return converter

    def _export_output(
        self, result: str
    ) -> Tuple[Optional[BaseModel], Optional[Dict[str, Any]]]:
        pydantic_output: Optional[BaseModel] = None
        json_output: Optional[Dict[str, Any]] = None

        if self.output_pydantic or self.output_json:
            model_output = self._convert_to_model(result)
            pydantic_output = (
                model_output if isinstance(model_output, BaseModel) else None
            )
            if isinstance(model_output, str):
                try:
                    json_output = json.loads(model_output)
                except json.JSONDecodeError:
                    json_output = None
            else:
                json_output = model_output if isinstance(model_output, dict) else None

        return pydantic_output, json_output

    def _convert_to_model(self, result: str) -> Union[dict, BaseModel, str]:
        model = self.output_pydantic or self.output_json
        if model is None:
            return result

        try:
            return self._validate_model(result, model)
        except Exception:
            return self._handle_partial_json(result, model)

    def _validate_model(
        self, result: str, model: Type[BaseModel]
    ) -> Union[dict, BaseModel]:
        exported_result = model.model_validate_json(result)
        if self.output_json:
            return exported_result.model_dump()
        return exported_result

    def _handle_partial_json(
        self, result: str, model: Type[BaseModel]
    ) -> Union[dict, BaseModel, str]:
        match = re.search(r"({.*})", result, re.DOTALL)
        if match:
            try:
                exported_result = model.model_validate_json(match.group(0))
                if self.output_json:
                    return exported_result.model_dump()
                return exported_result
            except Exception:
                pass

        return self._convert_with_instructions(result, model)

    def _convert_with_instructions(
        self, result: str, model: Type[BaseModel]
    ) -> Union[dict, BaseModel, str]:
        llm = self.agent.function_calling_llm or self.agent.llm  # type: ignore # “BaseAgent | None”的项目“None”没有属性“function_calling_llm”
        instructions = self._get_conversion_instructions(model, llm)

        converter = self._create_converter(
            llm=llm, text=result, model=model, instructions=instructions
        )
        exported_result = (
            converter.to_pydantic() if self.output_pydantic else converter.to_json()
        )

        if isinstance(exported_result, ConverterError):
            Printer().print(
                content=f"{exported_result.message} 使用原始输出。",
                color="red",
            )
            return result

        return exported_result

    def _get_output_format(self) -> OutputFormat:
        if self.output_json:
            return OutputFormat.JSON
        if self.output_pydantic:
            return OutputFormat.PYDANTIC
        return OutputFormat.RAW

    def _get_conversion_instructions(self, model: Type[BaseModel], llm: Any) -> str:
        instructions = "我要将此原始文本转换为有效的 JSON。"
        if not self._is_gpt(llm):
            model_schema = PydanticSchemaParser(model=model).get_schema()
            instructions = f"{instructions}\n\nJSON 应具有以下结构，并具有以下键：\n{model_schema}"
        return instructions

    def _save_output(self, content: str) -> None:
        if not self.output_file:
            raise Exception("未设置输出文件路径。")

        directory = os.path.dirname(self.output_file)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        with open(self.output_file, "w", encoding="utf-8") as file:
            file.write(content)

    def _is_gpt(self, llm) -> bool:
        return isinstance(llm, ChatOpenAI) and llm.openai_api_base is None

    def _save_file(self, result: Any) -> None:
        directory = os.path.dirname(self.output_file)  # type: ignore # “dirname”的类型变量“AnyOrLiteralStr”的值不能为“str | None”

        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        with open(self.output_file, "w", encoding="utf-8") as file:  # type: ignore # 传递给“open”的参数 1 的类型“str | None”与“int | str | bytes | PathLike[str] | PathLike[bytes]”不兼容
            file.write(result)
        return None

    def __repr__(self):
        return f"Task(description={self.description}, expected_output={self.expected_output})"
