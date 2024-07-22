from typing import List

from pydantic import BaseModel

from crewai.agent import Agent
from crewai.task import Task


class PlannerTaskPydanticOutput(BaseModel):
    """
    规划器任务 Pydantic 输出模型。
    """
    list_of_plans_per_task: List[str]  # 每个任务的计划列表


class CrewPlanner:
    """
    团队规划器类，用于协调多个 Agent 完成任务。
    """

    def __init__(self, tasks: List[Task]):
        """
        初始化 CrewPlanner。

        Args:
            tasks: 任务列表。
        """
        self.tasks = tasks

    def _handle_crew_planning(self):
        """
        处理团队规划，为每个任务创建详细的分步计划。
        """
        planning_agent = self._create_planning_agent()  # 创建规划 Agent
        tasks_summary = self._create_tasks_summary()  # 创建任务摘要

        planner_task = self._create_planner_task(planning_agent, tasks_summary)  # 创建规划任务

        return planner_task.execute_sync()  # 执行规划任务并返回结果

    def _create_planning_agent(self) -> Agent:
        """
        创建用于团队规划的规划 Agent。
        """
        return Agent(
            role="任务执行规划器",
            goal=(
                "你的目标是根据每个 Agent 可用的任务和工具创建一个极其详细的分步计划，"
                "以便他们能够以 exemplary 的方式执行任务"
            ),
            backstory="团队规划的规划 Agent",
        )

    def _create_planner_task(self, planning_agent: Agent, tasks_summary: str) -> Task:
        """
        使用给定的 Agent 和任务摘要创建规划任务。
        """
        return Task(
            description=(
                f"根据以下任务摘要：{tasks_summary} \n"
                "根据任务描述、可用工具和 Agent 的目标创建最描述性的计划，"
                "以便他们能够完美地执行目标。"
            ),
            expected_output="关于 Agent 如何使用可用工具熟练执行任务的分步计划",
            agent=planning_agent,
            output_pydantic=PlannerTaskPydanticOutput,
        )

    def _create_tasks_summary(self) -> str:
        """
        创建所有任务的摘要。
        """
        tasks_summary = []
        for idx, task in enumerate(self.tasks):
            tasks_summary.append(
                f"""
                任务编号 {idx + 1} - {task.description}
                "task_description": {task.description}
                "task_expected_output": {task.expected_output}
                "agent": {task.agent.role if task.agent else "None"}
                "agent_goal": {task.agent.goal if task.agent else "None"}
                "task_tools": {task.tools}
                "agent_tools": {task.agent.tools if task.agent else "None"}
                """
            )
        return " ".join(tasks_summary)
