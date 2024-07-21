from langchain.tools import StructuredTool
from pydantic import BaseModel, ConfigDict, Field

from crewai.agents.cache import CacheHandler


class CacheTools(BaseModel):
    """用于访问缓存的默认工具。"""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    name: str = "访问缓存"
    cache_handler: CacheHandler = Field(
        description="团队的缓存处理程序",
        default=CacheHandler(),
    )

    def tool(self):
        return StructuredTool.from_function(
            func=self.hit_cache,
            name=self.name,
            description="直接从缓存中读取",
        )

    def hit_cache(self, key):
        split = key.split("tool:")
        tool = split[1].split("|input:")[0].strip()
        tool_input = split[1].split("|input:")[1].strip()
        return self.cache_handler.read(tool, tool_input)
