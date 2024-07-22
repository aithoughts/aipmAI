import json
from typing import Any, List, Type, Union

import regex
from langchain.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException
from langchain_core.outputs import Generation
from langchain_core.pydantic_v1 import ValidationError
from pydantic import BaseModel
from pydantic.v1 import BaseModel as V1BaseModel


class CrewPydanticOutputParser(PydanticOutputParser):
    """将文本解析为 Pydantic 模型的解析器。"""

    pydantic_object: Union[Type[BaseModel], Type[V1BaseModel]]  # Pydantic 模型类型

    def parse_result(self, result: List[Generation], *, partial: bool = False) -> Any:
        """解析结果，将文本转换为 Pydantic 模型。"""
        result[0].text = self._transform_in_valid_json(result[0].text)  # 转换文本为有效的 JSON

        # 处理函数调用 LLM 返回名称而不是 tool_name 的边缘情况
        json_object = json.loads(result[0].text)
        json_object["tool_name"] = (
            json_object["name"]
            if "tool_name" not in json_object
            else json_object["tool_name"]
        )
        result[0].text = json.dumps(json_object)

        json_object = super().parse_result(result)  # 使用父类的解析方法
        try:
            return self.pydantic_object.parse_obj(json_object)  # 将 JSON 对象解析为 Pydantic 模型
        except ValidationError as e:
            name = self.pydantic_object.__name__  # 获取 Pydantic 模型名称
            msg = f"无法从完成结果 {json_object} 中解析 {name}。错误：{e}"
            raise OutputParserException(msg, llm_output=json_object)  # 抛出解析错误

    def _transform_in_valid_json(self, text) -> str:
        """将文本转换为有效的 JSON 格式。"""
        text = text.replace("```", "").replace("json", "")  # 移除干扰字符
        json_pattern = r"\{(?:[^{}]|(?R))*\}"  # JSON 模式
        matches = regex.finditer(json_pattern, text)  # 查找匹配的 JSON 对象

        for match in matches:
            try:
                # 尝试将匹配的字符串解析为 JSON
                json_obj = json.loads(match.group())
                # 返回第一个成功解析的 JSON 对象
                json_obj = json.dumps(json_obj)
                return str(json_obj)
            except json.JSONDecodeError:
                # 如果解析失败，则跳过到下一个匹配项
                continue
        return text  # 如果没有找到有效的 JSON 对象，则返回原始文本
