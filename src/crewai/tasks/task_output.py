import json
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, model_validator

from crewai.tasks.output_format import OutputFormat


class TaskOutput(BaseModel):
    """表示任务结果的类。"""

    description: str = Field(description="任务描述")
    summary: Optional[str] = Field(description="任务摘要", default=None)
    raw: str = Field(description="任务的原始输出", default="")
    pydantic: Optional[BaseModel] = Field(
        description="任务的 Pydantic 输出", default=None
    )
    json_dict: Optional[Dict[str, Any]] = Field(
        description="任务的 JSON 字典", default=None
    )
    agent: str = Field(description="执行任务的代理")
    output_format: OutputFormat = Field(
        description="任务的输出格式", default=OutputFormat.RAW
    )

    @model_validator(mode="after")
    def set_summary(self):
        """根据描述设置摘要字段。"""
        excerpt = " ".join(self.description.split(" ")[:10])
        self.summary = f"{excerpt}..."
        return self

    @property
    def json(self) -> Optional[str]:
        if self.output_format != OutputFormat.JSON:
            raise ValueError(
                """
                请求的输出格式无效。
                如果要访问 JSON 输出，
                请确保为任务设置 output_json 属性
                """
            )

        return json.dumps(self.json_dict)

    def to_dict(self) -> Dict[str, Any]:
        """将 json_output 和 pydantic_output 转换为字典。"""
        output_dict = {}
        if self.json_dict:
            output_dict.update(self.json_dict)
        elif self.pydantic:
            output_dict.update(self.pydantic.model_dump())
        return output_dict

    def __str__(self) -> str:
        if self.pydantic:
            return str(self.pydantic)
        if self.json_dict:
            return str(self.json_dict)
        return self.raw
