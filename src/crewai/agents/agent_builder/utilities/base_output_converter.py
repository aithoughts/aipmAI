from abc import ABC, abstractmethod
from typing import Any, Optional

from pydantic import BaseModel, Field


class OutputConverter(BaseModel, ABC):
    """
    用于将任务结果转换为结构化格式的抽象基类。

    此类提供了一个框架，用于根据特定代理的要求将非结构化文本转换为
    Pydantic 模型或 JSON。它使用语言模型根据给定的指令解释和构建输入文本。

    属性：
        text (str): 要转换的输入文本。
        llm (Any): 用于转换的语言模型。
        model (Any): 用于构建输出的目标模型。
        instructions (str): 转换过程的具体指令。
        max_attempts (int): 转换尝试的最大次数（默认值：3）。
    """

    text: str = Field(description="要转换的文本。")
    llm: Any = Field(description="用于转换文本的语言模型。")
    model: Any = Field(description="用于转换文本的模型。")
    instructions: str = Field(description="给 LLM 的转换指令。")
    max_attempts: Optional[int] = Field(
        description="尝试获取格式化输出的最大次数。",
        default=3,
    )

    @abstractmethod
    def to_pydantic(self, current_attempt=1):
        """将文本转换为 pydantic。"""
        pass

    @abstractmethod
    def to_json(self, current_attempt=1):
        """将文本转换为 json。"""
        pass

    @property
    @abstractmethod
    def is_gpt(self) -> bool:
        """返回提供的 llm 是否来自 openai 的 gpt。"""
        pass