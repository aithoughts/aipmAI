from typing import Any, ClassVar, Optional

from langchain.prompts import BasePromptTemplate, PromptTemplate
from pydantic import BaseModel, Field

from crewai.utilities import I18N


class Prompts(BaseModel):
    """
    管理并生成通用 Agent 的提示。
    """

    i18n: I18N = Field(default=I18N())  # 国际化工具
    tools: list[Any] = Field(default=[])  # 工具列表
    system_template: Optional[str] = None  # 系统提示模板
    prompt_template: Optional[str] = None  # 用户提示模板
    response_template: Optional[str] = None  # 响应模板
    SCRATCHPAD_SLICE: ClassVar[str] = "\n{agent_scratchpad}"  # 草稿区占位符

    def task_execution(self) -> BasePromptTemplate:
        """
        生成用于任务执行的标准提示。
        """
        slices = ["role_playing"]  # 提示组件列表，初始包含"role_playing"
        if len(self.tools) > 0:
            slices.append("tools")  # 如果有工具，添加"tools"组件
        else:
            slices.append("no_tools")  # 否则添加"no_tools"组件

        slices.append("task")  # 添加"task"组件

        # 根据是否有自定义模板选择构建方式
        if not self.system_template and not self.prompt_template:
            return self._build_prompt(slices)  # 使用默认模板构建
        else:
            return self._build_prompt(
                slices,
                self.system_template,
                self.prompt_template,
                self.response_template,
            )  # 使用自定义模板构建

    def _build_prompt(
        self,
        components: list[str],
        system_template=None,
        prompt_template=None,
        response_template=None,
    ) -> BasePromptTemplate:
        """
        根据指定的组件构建提示字符串。
        """
        # 未提供自定义模板时使用默认模板
        if not system_template and not prompt_template:
            prompt_parts = [
                self.i18n.slice(component) for component in components
            ]  # 获取每个组件的国际化内容
            prompt_parts.append(
                self.SCRATCHPAD_SLICE
            )  # 添加草稿区占位符
            prompt = PromptTemplate.from_template(
                "".join(prompt_parts)
            )  # 创建 PromptTemplate 对象
        # 提供自定义模板时使用自定义模板
        else:
            prompt_parts = [
                self.i18n.slice(component)
                for component in components
                if component != "task"
            ]  # 获取除"task"组件外的国际化内容
            system = system_template.replace(
                "{{ .System }}", "".join(prompt_parts)
            )  # 替换系统提示模板中的占位符
            prompt = prompt_template.replace(
                "{{ .Prompt }}",
                "".join([self.i18n.slice("task"), self.SCRATCHPAD_SLICE]),
            )  # 替换用户提示模板中的占位符
            response = response_template.split("{{ .Response }}")[
                0
            ]  # 获取响应模板的开头部分
            prompt = PromptTemplate.from_template(
                f"{system}\n{prompt}\n{response}"
            )  # 创建 PromptTemplate 对象
        return prompt
