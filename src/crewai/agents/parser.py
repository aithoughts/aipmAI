import re
from typing import Any, Union

from json_repair import repair_json
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.exceptions import OutputParserException

from crewai.utilities import I18N

FINAL_ANSWER_ACTION = "Final Answer:"
MISSING_ACTION_AFTER_THOUGHT_ERROR_MESSAGE = (
    "我做错了。格式无效：我在“Thought:”之后缺少“Action:”。"
    "我接下来会做对，并且不要使用我已经使用过的工具。\n"
)
MISSING_ACTION_INPUT_AFTER_ACTION_ERROR_MESSAGE = (
    "我做错了。格式无效：我在“Action:”之后缺少“Action Input:”。"
    "我接下来会做对，并且不要使用我已经使用过的工具。\n"
)
FINAL_ANSWER_AND_PARSABLE_ACTION_ERROR_MESSAGE = (
    "我做错了。试图同时执行操作和给出最终答案，我必须要么执行操作，要么给出最终答案。"
)


class CrewAgentParser(ReActSingleInputOutputParser):
    """解析具有单个工具输入的 ReAct 风格的 LLM 调用。

    期望输出采用以下两种格式之一。

    如果输出表示应采取行动，
    则应采用以下格式。这将导致返回 AgentAction。

    Thought: 代理在这里思考
    Action: 搜索
    Action Input: 广州的温度是多少？

    如果输出表示应给出最终答案，
    则应采用以下格式。这将导致返回 AgentFinish。

    Thought: 代理在这里思考
    Final Answer: 温度是 36 摄氏度
    """

    _i18n: I18N = I18N()
    agent: Any = None

    def parse(self, text: str) -> Union[AgentAction, AgentFinish]:
        includes_answer = FINAL_ANSWER_ACTION in text
        regex = r"Action\s*\d*\s*:[\s]*(.*?)[\s]*Action\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)"
        action_match = re.search(regex, text, re.DOTALL)
        if action_match:
            if includes_answer:
                raise OutputParserException(
                    f"{FINAL_ANSWER_AND_PARSABLE_ACTION_ERROR_MESSAGE}: {text}"
                )
            action = action_match.group(1)
            clean_action = self._clean_action(action)

            action_input = action_match.group(2).strip()

            tool_input = action_input.strip(" ").strip('"')
            safe_tool_input = self._safe_repair_json(tool_input)

            return AgentAction(clean_action, safe_tool_input, text)

        elif includes_answer:
            return AgentFinish(
                {"output": text.split(FINAL_ANSWER_ACTION)[-1].strip()}, text
            )

        if not re.search(r"Action\s*\d*\s*:[\s]*(.*?)", text, re.DOTALL):
            self.agent.increment_formatting_errors()
            raise OutputParserException(
                f"无法解析 LLM 输出：`{text}`",
                observation=f"{MISSING_ACTION_AFTER_THOUGHT_ERROR_MESSAGE}\n{self._i18n.slice('final_answer_format')}",
                llm_output=text,
                send_to_llm=True,
            )
        elif not re.search(
            r"[\s]*Action\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)", text, re.DOTALL
        ):
            self.agent.increment_formatting_errors()
            raise OutputParserException(
                f"无法解析 LLM 输出：`{text}`",
                observation=MISSING_ACTION_INPUT_AFTER_ACTION_ERROR_MESSAGE,
                llm_output=text,
                send_to_llm=True,
            )
        else:
            format = self._i18n.slice("format_without_tools")
            error = f"{format}"
            self.agent.increment_formatting_errors()
            raise OutputParserException(
                error,
                observation=error,
                llm_output=text,
                send_to_llm=True,
            )

    def _clean_action(self, text: str) -> str:
        """通过删除不必要的格式字符来清理操作字符串。"""
        return re.sub(r"^\s*\*+\s*|\s*\*+\s*$", "", text).strip()

    def _safe_repair_json(self, tool_input: str) -> str:
        UNABLE_TO_REPAIR_JSON_RESULTS = ['""', "{}"]

        # 如果输入以方括号开头和结尾，则跳过修复
        # 说明：JSON 解析器在处理用方括号 ('[]') 括起来的输入时存在问题。
        # 这些通常是有效的 JSON 数组或字符串，不需要修复。尝试修复此类输入
        # 可能会导致意外的更改，例如将整个输入包装在其他层中或修改
        # 结构以改变其含义。通过跳过对以方括号开头和结尾的输入的修复，我们可以保留这些有效 JSON 结构的完整性，并避免不必要的修改。
        if tool_input.startswith("[") and tool_input.endswith("]"):
            return tool_input

        # 在修复之前，处理常见的 LLM 问题：
        # 1. 将 """ 替换为 " 以避免 JSON 解析器错误

        tool_input = tool_input.replace('"""', '"')

        result = repair_json(tool_input)
        if result in UNABLE_TO_REPAIR_JSON_RESULTS:
            return tool_input

        return str(result)
