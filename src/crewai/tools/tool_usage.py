import ast
from difflib import SequenceMatcher
from textwrap import dedent
from typing import Any, List, Union

from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI

from crewai.agents.tools_handler import ToolsHandler
from crewai.telemetry import Telemetry
from crewai.tools.tool_calling import InstructorToolCalling, ToolCalling
from crewai.utilities import I18N, Converter, ConverterError, Printer

try:
    import agentops
except ImportError:
    agentops = None

OPENAI_BIGGER_MODELS = ["gpt-4"]


class ToolUsageErrorException(Exception):
    """工具使用中发生错误时引发的异常。"""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class ToolUsage:
    """
    表示代理使用工具的类。

    属性：
      task: 正在执行的任务。
      tools_handler: 将管理工具使用的工具处理程序。
      tools: 代理可用的工具列表。
      original_tools: 转换为 BaseTool 之前代理可用的原始工具。
      tools_description: 代理可用工具的描述。
      tools_names: 代理可用工具的名称。
      function_calling_llm: 用于工具使用的语言模型。
    """

    def __init__(
        self,
        tools_handler: ToolsHandler,
        tools: List[BaseTool],
        original_tools: List[Any],
        tools_description: str,
        tools_names: str,
        task: Any,
        function_calling_llm: Any,
        agent: Any,
        action: Any,
    ) -> None:
        self._i18n: I18N = I18N()
        self._printer: Printer = Printer()
        # self._telemetry: Telemetry = Telemetry()
        self._run_attempts: int = 1
        self._max_parsing_attempts: int = 3
        self._remember_format_after_usages: int = 3
        self.agent = agent
        self.tools_description = tools_description
        self.tools_names = tools_names
        self.tools_handler = tools_handler
        self.original_tools = original_tools
        self.tools = tools
        self.task = task
        self.action = action
        self.function_calling_llm = function_calling_llm

        # 为更大的模型设置最大解析尝试次数
        if (isinstance(self.function_calling_llm, ChatOpenAI)) and (
            self.function_calling_llm.openai_api_base is None
        ):
            if self.function_calling_llm.model_name in OPENAI_BIGGER_MODELS:
                self._max_parsing_attempts = 2
                self._remember_format_after_usages = 4

    def parse(self, tool_string: str):
        """解析工具字符串并返回工具调用。"""
        return self._tool_calling(tool_string)

    def use(
        self, calling: Union[ToolCalling, InstructorToolCalling], tool_string: str
    ) -> str:
        if isinstance(calling, ToolUsageErrorException):
            error = calling.message
            self._printer.print(content=f"\n\n{error}\n", color="red")
            self.task.increment_tools_errors()
            return error

        # BUG? 下面的代码似乎无法访问
        try:
            tool = self._select_tool(calling.tool_name)
        except Exception as e:
            error = getattr(e, "message", str(e))
            self.task.increment_tools_errors()
            self._printer.print(content=f"\n\n{error}\n", color="red")
            return error
        return f"{self._use(tool_string=tool_string, tool=tool, calling=calling)}"  # type: ignore # BUG?: "ToolUsage" 的 "_use" 不返回值（它只返回 None）

    def _use(
        self,
        tool_string: str,
        tool: BaseTool,
        calling: Union[ToolCalling, InstructorToolCalling],
    ) -> str:  # TODO: 修复此返回类型
        tool_event = agentops.ToolEvent(name=calling.tool_name) if agentops else None
        if self._check_tool_repeated_usage(calling=calling):  # type: ignore # "ToolUsage" 的 "_check_tool_repeated_usage" 不返回值（它只返回 None）
            try:
                result = self._i18n.errors("task_repeated_usage").format(
                    tool_names=self.tools_names
                )
                self._printer.print(content=f"\n\n{result}\n", color="purple")
                # self._telemetry.tool_repeated_usage(
                #     llm=self.function_calling_llm,
                #     tool_name=tool.name,
                #     attempts=self._run_attempts,
                # )
                result = self._format_result(result=result)  # type: ignore # "ToolUsage" 的 "_format_result" 不返回值（它只返回 None）
                return result  # type: ignore # 修复此函数的返回类型

            except Exception:
                self.task.increment_tools_errors()

        result = None  # type: ignore #  赋值中的类型不兼容（表达式类型为“None”，变量类型为“str”）

        if self.tools_handler.cache:
            result = self.tools_handler.cache.read(  # type: ignore # 赋值中的类型不兼容（表达式类型为“str | None”，变量类型为“str”）
                tool=calling.tool_name, input=calling.arguments
            )

        original_tool = next(
            (ot for ot in self.original_tools if ot.name == tool.name), None
        )

        if result is None: #! finecwg: if not result --> if result is None
            try:
                if calling.tool_name in [
                    "Delegate work to coworker",
                    "Ask question to coworker",
                ]:
                    self.task.increment_delegations()

                if calling.arguments:
                    try:
                        acceptable_args = tool.args_schema.schema()["properties"].keys()  # type: ignore # “type[BaseModel] | None”类型的项目“None”没有属性“schema”
                        arguments = {
                            k: v
                            for k, v in calling.arguments.items()
                            if k in acceptable_args
                        }
                        result = tool.invoke(input=arguments)
                    except Exception:
                        arguments = calling.arguments
                        result = tool.invoke(input=arguments)
                else:
                    result = tool.invoke(input={})
            except Exception as e:
                self._run_attempts += 1
                if self._run_attempts > self._max_parsing_attempts:
                    # self._telemetry.tool_usage_error(llm=self.function_calling_llm)
                    error_message = self._i18n.errors("tool_usage_exception").format(
                        error=e, tool=tool.name, tool_inputs=tool.description
                    )
                    error = ToolUsageErrorException(
                        f'\n{error_message}.\n继续。 {self._i18n.slice("format").format(tool_names=self.tools_names)}'  # 翻译字符串
                    ).message
                    self.task.increment_tools_errors()
                    self._printer.print(content=f"\n\n{error_message}\n", color="red")
                    return error  # type: ignore #  不期望返回值

                self.task.increment_tools_errors()
                if agentops:
                    agentops.record(
                        agentops.ErrorEvent(exception=e, trigger_event=tool_event)
                    )
                return self.use(calling=calling, tool_string=tool_string)  # type: ignore #  不期望返回值

            if self.tools_handler:
                should_cache = True
                if (
                    hasattr(original_tool, "cache_function")
                    and original_tool.cache_function  # type: ignore # “Any | None”类型的项目“None”没有属性“cache_function”
                ):
                    should_cache = original_tool.cache_function(  # type: ignore # “Any | None”类型的项目“None”没有属性“cache_function”
                        calling.arguments, result
                    )

                self.tools_handler.on_tool_use(
                    calling=calling, output=result, should_cache=should_cache
                )

        self._printer.print(content=f"\n\n{result}\n", color="purple")
        if agentops:
            agentops.record(tool_event)
        # self._telemetry.tool_usage(
        #     llm=self.function_calling_llm,
        #     tool_name=tool.name,
        #     attempts=self._run_attempts,
        # )
        result = self._format_result(result=result)  # type: ignore # "ToolUsage" 的 "_format_result" 不返回值（它只返回 None）
        data = {
            "result": result,
            "tool_name": tool.name,
            "tool_args": calling.arguments,
        }

        if (
            hasattr(original_tool, "result_as_answer")
            and original_tool.result_as_answer  # type: ignore # “Any | None”类型的项目“None”没有属性“cache_function”
        ):
            result_as_answer = original_tool.result_as_answer  # type: ignore # “Any | None”类型的项目“None”没有属性“result_as_answer”
            data["result_as_answer"] = result_as_answer

        self.agent.tools_results.append(data)

        return result  # type: ignore #  不期望返回值

    def _format_result(self, result: Any) -> None:
        self.task.used_tools += 1
        if self._should_remember_format():  # type: ignore # "ToolUsage" 的 "_should_remember_format" 不返回值（它只返回 None）
            result = self._remember_format(result=result)  # type: ignore # "ToolUsage" 的 "_remember_format" 不返回值（它只返回 None）
        return result

    def _should_remember_format(self) -> None:
        return self.task.used_tools % self._remember_format_after_usages == 0

    def _remember_format(self, result: str) -> None:
        result = str(result)
        result += "\n\n" + self._i18n.slice("tools").format(
            tools=self.tools_description, tool_names=self.tools_names
        )
        return result  # type: ignore #  不期望返回值

    def _check_tool_repeated_usage(
        self, calling: Union[ToolCalling, InstructorToolCalling]
    ) -> None:
        if not self.tools_handler:
            return False  # type: ignore #  不期望返回值
        if last_tool_usage := self.tools_handler.last_used_tool:
            return (calling.tool_name == last_tool_usage.tool_name) and (  # type: ignore #  不期望返回值
                calling.arguments == last_tool_usage.arguments
            )

    def _select_tool(self, tool_name: str) -> BaseTool:
        order_tools = sorted(
            self.tools,
            key=lambda tool: SequenceMatcher(
                None, tool.name.lower().strip(), tool_name.lower().strip()
            ).ratio(),
            reverse=True,
        )
        for tool in order_tools:
            if (
                tool.name.lower().strip() == tool_name.lower().strip()
                or SequenceMatcher(
                    None, tool.name.lower().strip(), tool_name.lower().strip()
                ).ratio()
                > 0.85
            ):
                return tool
        self.task.increment_tools_errors()
        if tool_name and tool_name != "":
            raise Exception(
                f"操作 '{tool_name}' 不存在，这些是唯一可用的操作：\n {self.tools_description}"
            )
        else:
            raise Exception(
                f"我不记得操作名称了，这些是唯一可用的操作： {self.tools_description}"
            )

    def _render(self) -> str:
        """以纯文本形式呈现工具名称和描述。"""
        descriptions = []
        for tool in self.tools:
            args = {
                k: {k2: v2 for k2, v2 in v.items() if k2 in ["description", "type"]}
                for k, v in tool.args.items()
            }
            descriptions.append(
                "\n".join(
                    [
                        f"工具名称：{tool.name.lower()}",
                        f"工具描述：{tool.description}",
                        f"工具参数：{args}",
                    ]
                )
            )
        return "\n--\n".join(descriptions)

    def _is_gpt(self, llm) -> bool:
        return isinstance(llm, ChatOpenAI) and llm.openai_api_base is None

    def _tool_calling(
        self, tool_string: str
    ) -> Union[ToolCalling, InstructorToolCalling]:
        try:
            if self.function_calling_llm:
                model = (
                    InstructorToolCalling
                    if self._is_gpt(self.function_calling_llm)
                    else ToolCalling
                )
                converter = Converter(
                    text=f"只有以下工具可用：\n###\n{self._render()}\n\n返回工具的有效模式，工具名称必须与选项之一完全相同，使用此文本通知有效的输出模式：\n\n{tool_string}```",  # 翻译字符串
                    llm=self.function_calling_llm,
                    model=model,
                    instructions=dedent(
                        """\
              该模式应具有以下结构，只有两个键：
              - tool_name: str
              - arguments: dict（传递所有参数）

              示例：
              {"tool_name": "工具名称", "arguments": {"arg_name1": "值", "arg_name2": 2}}""",
                    ),
                    max_attempts=1,
                )
                calling = converter.to_pydantic()

                if isinstance(calling, ConverterError):
                    raise calling
            else:
                tool_name = self.action.tool
                tool = self._select_tool(tool_name)
                try:
                    tool_input = self._validate_tool_input(self.action.tool_input)
                    arguments = ast.literal_eval(tool_input)
                except Exception:
                    return ToolUsageErrorException(  # type: ignore # 不兼容的返回值类型（获取“ToolUsageErrorException”，预期为“ToolCalling | InstructorToolCalling”）
                        f'{self._i18n.errors("tool_arguments_error")}'
                    )
                if not isinstance(arguments, dict):
                    return ToolUsageErrorException(  # type: ignore # 不兼容的返回值类型（获取“ToolUsageErrorException”，预期为“ToolCalling | InstructorToolCalling”）
                        f'{self._i18n.errors("tool_arguments_error")}'
                    )
                calling = ToolCalling(  # type: ignore # “ToolCalling”的意外关键字参数“log”
                    tool_name=tool.name,
                    arguments=arguments,
                    log=tool_string,
                )
        except Exception as e:
            self._run_attempts += 1
            if self._run_attempts > self._max_parsing_attempts:
                # self._telemetry.tool_usage_error(llm=self.function_calling_llm)
                self.task.increment_tools_errors()
                self._printer.print(content=f"\n\n{e}\n", color="red")
                return ToolUsageErrorException(  # type: ignore # 不兼容的返回值类型（获取“ToolUsageErrorException”，预期为“ToolCalling | InstructorToolCalling”）
                    f'{self._i18n.errors("tool_usage_error").format(error=e)}\n继续。 {self._i18n.slice("format").format(tool_names=self.tools_names)}'  # 翻译字符串
                )
            return self._tool_calling(tool_string)

        return calling

    def _validate_tool_input(self, tool_input: str) -> str:
        try:
            ast.literal_eval(tool_input)
            return tool_input
        except Exception:
            # 清理并确保字符串正确地包含在大括号中
            tool_input = tool_input.strip()
            if not tool_input.startswith("{"):
                tool_input = "{" + tool_input
            if not tool_input.endswith("}"):
                tool_input += "}"

            # 手动将输入拆分为键值对
            entries = tool_input.strip("{} ").split(",")
            formatted_entries = []

            for entry in entries:
                if ":" not in entry:
                    continue  # 跳过格式错误的条目
                key, value = entry.split(":", 1)

                # 删除无关的空格和引号，替换单引号
                key = key.strip().strip('"').replace("'", '"')
                value = value.strip()

                # 处理替换值字符串开头和结尾处的单引号
                if value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]  # 删除单引号
                    value = (
                        '"' + value.replace('"', '\\"') + '"'
                    )  # 用双引号重新封装
                elif value.isdigit():  # 检查值是否为数字，因此为整数
                    formatted_value = value
                elif value.lower() in [
                    "true",
                    "false",
                    "null",
                ]:  # 检查布尔值和空值
                    formatted_value = value.lower()
                else:
                    # 假设该值为字符串，需要用引号引起来
                    formatted_value = '"' + value.replace('"', '\\"') + '"'

                # 使用正确的引号重建条目
                formatted_entry = f'"{key}": {formatted_value}'
                formatted_entries.append(formatted_entry)

            # 重建 JSON 字符串
            new_json_string = "{" + ", ".join(formatted_entries) + "}"
            return new_json_string
