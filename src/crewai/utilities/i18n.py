import json
import os
from typing import Dict, Optional

from pydantic import BaseModel, Field, PrivateAttr, model_validator


class I18N(BaseModel):
    """
    国际化类，用于加载和管理提示信息。
    """
    _prompts: Dict[str, Dict[str, str]] = PrivateAttr()  # 私有属性，用于存储加载的提示信息
    prompt_file: Optional[str] = Field(
        default=None,
        description="要加载的提示文件路径",
    )

    @model_validator(mode="after")
    def load_prompts(self) -> "I18N":
        """从 JSON 文件加载提示信息。"""
        try:
            if self.prompt_file:  # 如果指定了提示文件路径
                with open(self.prompt_file, "r") as f:
                    self._prompts = json.load(f)  # 从文件加载提示信息
            else:  # 如果没有指定提示文件路径，则使用默认路径
                dir_path = os.path.dirname(os.path.realpath(__file__))  # 获取当前文件所在目录
                prompts_path = os.path.join(dir_path, "../translations/zh.json")  # 默认提示文件路径

                with open(prompts_path, "r") as f:
                    self._prompts = json.load(f)  # 从默认路径加载提示信息
        except FileNotFoundError:
            raise Exception(f"提示文件 '{self.prompt_file}' 未找到。")
        except json.JSONDecodeError:
            raise Exception("从提示文件解码 JSON 时出错。")

        if not self._prompts:  # 如果提示信息为空
            self._prompts = {}  # 初始化为空字典

        return self

    def slice(self, slice: str) -> str:
        """获取指定切片类型的提示信息。"""
        return self.retrieve("slices", slice)

    def errors(self, error: str) -> str:
        """获取指定错误类型的提示信息。"""
        return self.retrieve("errors", error)

    def tools(self, error: str) -> str:
        """获取指定工具类型的提示信息。"""
        return self.retrieve("tools", error)

    def retrieve(self, kind, key) -> str:
        """从提示信息字典中获取指定类型的提示信息。"""
        try:
            return self._prompts[kind][key]  # 获取指定类型的提示信息
        except Exception as _:
            raise Exception(f"未找到 '{kind}':'{key}' 的提示信息。")
