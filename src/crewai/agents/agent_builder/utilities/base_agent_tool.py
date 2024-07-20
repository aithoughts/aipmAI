from abc import ABC, abstractmethod
from typing import List, Optional, Union

from pydantic import BaseModel, Field

from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.task import Task
from crewai.utilities import I18N


class BaseAgentTools(BaseModel, ABC):
    """默认的代理工具"""

    agents: List[BaseAgent] = Field(description="此团队中的代理列表。")
    i18n: I18N = Field(default=I18N(), description="国际化设置。")

    @abstractmethod
    def tools(self):
        pass

    def _get_coworker(self, coworker: Optional[str], **kwargs) -> Optional[str]:
        coworker = coworker or kwargs.get("co_worker") or kwargs.get("coworker")
        if coworker:
            is_list = coworker.startswith("[") and coworker.endswith("]")
            if is_list:
                coworker = coworker[1:-1].split(",")[0]

        return coworker

    def delegate_work(
        self, task: str, context: str, coworker: Optional[str] = None, **kwargs
    ):
        """用于将特定任务委托给同事，并传递所有必要的上下文和名称。"""
        coworker = self._get_coworker(coworker, **kwargs)
        return self._execute(coworker, task, context)

    def ask_question(
        self, question: str, context: str, coworker: Optional[str] = None, **kwargs
    ):
        """用于向同事询问问题、征求意见或获取信息，并传递所有必要的上下文和名称。"""
        coworker = self._get_coworker(coworker, **kwargs)
        return self._execute(coworker, question, context)

    def _execute(
        self, agent_name: Union[str, None], task: str, context: Union[str, None]
    ):
        """执行命令。"""
        try:
            if agent_name is None:
                agent_name = ""

            # 从代理名称中删除引号很重要。
            # 我们必须这样做的原因是，功能较弱的 LLM
            # 难以生成有效的 JSON。
            # 结果，我们最终得到了像这样被截断的无效 JSON：
            # {"task": "....", "coworker": "....
            # 而它应该是这样的：
            # {"task": "....", "coworker": "...."}
            agent_name = agent_name.casefold().replace('"', "").replace("\n", "")

            agent = [  # type: ignore # Incompatible types in assignment (expression has type "list[BaseAgent]", variable has type "str | None")
                available_agent
                for available_agent in self.agents
                if available_agent.role.casefold().replace("\n", "") == agent_name
            ]
        except Exception as _:
            return self.i18n.errors("agent_tool_unexsiting_coworker").format(
                coworkers="\n".join(
                    [f"- {agent.role.casefold()}" for agent in self.agents]
                )
            )

        if not agent:
            return self.i18n.errors("agent_tool_unexsiting_coworker").format(
                coworkers="\n".join(
                    [f"- {agent.role.casefold()}" for agent in self.agents]
                )
            )

        agent = agent[0]
        task_with_assigned_agent = Task(  # type: ignore # Incompatible types in assignment (expression has type "Task", variable has type "str")
            description=task,
            agent=agent,
            expected_output="考虑到共享的上下文，你对同事问你的这个问题的最佳答案是什么。",
        )
        return agent.execute_task(task_with_assigned_agent, context)
