import json
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from crewai.tasks.output_format import OutputFormat
from crewai.tasks.task_output import TaskOutput


class CrewOutput(BaseModel):
    """表示 Crew 结果的类。"""

    raw: str = Field(description="Crew 的原始输出", default="")
    pydantic: Optional[BaseModel] = Field(
        description="Crew 的 Pydantic 输出", default=None
    )
    json_dict: Optional[Dict[str, Any]] = Field(
        description="Crew 的 JSON 字典输出", default=None
    )
    tasks_output: list[TaskOutput] = Field(
        description="每个任务的输出", default=[]
    )
    token_usage: Dict[str, Any] = Field(
        description="已处理的 token 摘要", default={}
    )

    @property
    def json(self) -> Optional[str]:
        if self.tasks_output[-1].output_format != OutputFormat.JSON:
            raise ValueError(
                "在最终任务中未找到 JSON 输出。请确保在 Crew 的最终任务中设置 output_json 属性。"
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

    def __str__(self):
        if self.pydantic:
            return str(self.pydantic)
        if self.json_dict:
            return str(self.json_dict)
        return self.raw
