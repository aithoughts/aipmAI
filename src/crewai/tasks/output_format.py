from enum import Enum


class OutputFormat(str, Enum):
    """表示任务输出格式的枚举。"""

    JSON = "json"
    PYDANTIC = "pydantic"
    RAW = "raw"
