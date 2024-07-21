import json
from typing import Any, List

import regex
from langchain.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException
from langchain_core.outputs import Generation
from langchain_core.pydantic_v1 import ValidationError


class ToolOutputParser(PydanticOutputParser):
    """解析工具使用及其参数的函数调用。"""

    def parse_result(self, result: List[Generation], *, partial: bool = False) -> Any:
        result[0].text = self._transform_in_valid_json(result[0].text)
        json_object = super().parse_result(result)
        try:
            return self.pydantic_object.parse_obj(json_object)
        except ValidationError as e:
            name = self.pydantic_object.__name__
            msg = f"无法从 Completion {json_object} 中解析 {name}。得到：{e}"
            raise OutputParserException(msg, llm_output=json_object)

    def _transform_in_valid_json(self, text) -> str:
        """将文本转换为有效的 JSON 格式。"""
        text = text.replace("```", "").replace("json", "")
        json_pattern = r"\{(?:[^{}]|(?R))*\}"
        matches = regex.finditer(json_pattern, text)

        for match in matches:
            try:
                # 尝试将匹配的字符串解析为 JSON
                json_obj = json.loads(match.group())
                # 返回第一个成功解析的 JSON 对象
                json_obj = json.dumps(json_obj)
                return str(json_obj)
            except json.JSONDecodeError:
                # 如果解析失败，则跳到下一个匹配项
                continue
        return text
