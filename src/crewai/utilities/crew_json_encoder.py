from datetime import datetime
import json
from uuid import UUID
from pydantic import BaseModel


class CrewJSONEncoder(json.JSONEncoder):
    """自定义 JSON 编码器，用于处理 Pydantic 模型、UUID 和 datetime 对象。"""

    def default(self, obj):
        """定义如何编码自定义对象。"""
        if isinstance(obj, BaseModel):
            return self._handle_pydantic_model(obj)  # 处理 Pydantic 模型
        elif isinstance(obj, UUID):
            return str(obj)  # 将 UUID 转换为字符串
        elif isinstance(obj, datetime):
            return obj.isoformat()  # 将 datetime 对象转换为 ISO 格式字符串
        return super().default(obj)  # 对于其他对象，使用默认编码器

    def _handle_pydantic_model(self, obj):
        """处理 Pydantic 模型，避免循环引用。"""
        try:
            data = obj.model_dump()  # 将 Pydantic 模型转换为字典
            # 移除循环引用
            for key, value in data.items():
                if isinstance(value, BaseModel):
                    data[key] = str(
                        value
                    )  # 将嵌套的 Pydantic 模型转换为字符串表示
            return data
        except RecursionError:
            return str(
                obj
            )  # 如果检测到循环引用，则回退到字符串表示
