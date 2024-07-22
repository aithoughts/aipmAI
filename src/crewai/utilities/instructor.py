from typing import Any, Optional, Type

import instructor
from pydantic import BaseModel, Field, PrivateAttr, model_validator


class Instructor(BaseModel):
    """
    封装了 agent llm 与 instructor 的类。
    """

    _client: Any = PrivateAttr()  # 私有属性，用于存储 instructor 客户端
    content: str = Field(description="发送给 instructor 的内容。")
    agent: Optional[Any] = Field(
        description="需要使用 instructor 的 agent。", default=None
    )
    llm: Optional[Any] = Field(
        description="需要使用 instructor 的 agent。", default=None
    )
    instructions: Optional[str] = Field(
        description="发送给 instructor 的指令。", default=None
    )
    model: Type[BaseModel] = Field(
        description="用于创建输出的 Pydantic 模型。"
    )

    @model_validator(mode="after")
    def set_instructor(self):
        """设置 instructor。"""
        if self.agent and not self.llm:  # 如果 agent 存在，但 llm 不存在
            self.llm = self.agent.function_calling_llm or self.agent.llm  # 使用 agent 的 function_calling_llm 或 llm

        self._client = instructor.patch(  # 使用 instructor.patch 修改 llm 客户端
            self.llm.client._client,
            mode=instructor.Mode.TOOLS,  # 设置模式为 TOOLS
        )
        return self

    def to_json(self):
        """将 instructor 输出转换为 JSON 格式。"""
        model = self.to_pydantic()  # 将输出转换为 Pydantic 模型
        return model.model_dump_json(indent=2)  # 将 Pydantic 模型转换为 JSON 格式

    def to_pydantic(self):
        """将 instructor 输出转换为 Pydantic 模型。"""
        messages = [{"role": "user", "content": self.content}]  # 初始化消息列表
        if self.instructions:  # 如果存在指令
            messages.append({"role": "system", "content": self.instructions})  # 添加系统指令

        model = self._client.chat.completions.create(  # 使用 instructor 客户端创建完成请求
            model=self.llm.model_name,  # 指定模型名称
            response_model=self.model,  # 指定响应模型
            messages=messages  # 指定消息列表
        )
        return model
