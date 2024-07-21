from typing import Any, Dict, Optional

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field as PydanticField
from pydantic.v1 import BaseModel, Field


class ToolCalling(BaseModel):
    tool_name: str = Field(..., description="要调用的工具的名称。")
    arguments: Optional[Dict[str, Any]] = Field(
        ..., description="要传递给工具的参数字典。"
    )


class InstructorToolCalling(PydanticBaseModel):
    tool_name: str = PydanticField(
        ..., description="要调用的工具的名称。"
    )
    arguments: Optional[Dict[str, Any]] = PydanticField(
        ..., description="要传递给工具的参数字典。"
    )
