import json

from langchain.schema import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from crewai.agents.agent_builder.utilities.base_output_converter import OutputConverter


class ConverterError(Exception):
    """转换器在解析输入时发生的错误。"""

    def __init__(self, message: str, *args: object) -> None:
        super().__init__(message, *args)
        self.message = message


class Converter(OutputConverter):
    """将文本转换为 pydantic 或 json 的类。"""

    def to_pydantic(self, current_attempt=1):
        """将文本转换为 pydantic。"""
        try:
            if self.is_gpt:
                return self._create_instructor().to_pydantic()
            else:
                return self._create_chain().invoke({})
        except Exception as e:
            if current_attempt < self.max_attempts:
                return self.to_pydantic(current_attempt + 1)
            return ConverterError(
                f"由于以下错误，无法将文本转换为 pydantic 模型：{e}"
            )

    def to_json(self, current_attempt=1):
        """将文本转换为 json。"""
        try:
            if self.is_gpt:
                return self._create_instructor().to_json()
            else:
                return json.dumps(self._create_chain().invoke({}).model_dump())
        except Exception as e:
            if current_attempt < self.max_attempts:
                return self.to_json(current_attempt + 1)
            return ConverterError(f"无法将文本转换为 JSON，错误：{e}。")

    def _create_instructor(self):
        """创建指导者。"""
        from crewai.utilities import Instructor

        inst = Instructor(
            llm=self.llm,
            max_attempts=self.max_attempts,
            model=self.model,
            content=self.text,
            instructions=self.instructions,
        )
        return inst

    def _create_chain(self):
        """创建链。"""
        from crewai.utilities.crew_pydantic_output_parser import (
            CrewPydanticOutputParser,
        )

        parser = CrewPydanticOutputParser(pydantic_object=self.model)
        new_prompt = SystemMessage(content=self.instructions) + HumanMessage(
            content=self.text
        )
        return new_prompt | self.llm | parser

    @property
    def is_gpt(self) -> bool:
        """返回提供的 llm 是否来自 openai 的 gpt。"""
        return isinstance(self.llm, ChatOpenAI) and self.llm.openai_api_base is None
