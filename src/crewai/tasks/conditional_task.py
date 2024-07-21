from typing import Any, Callable

from pydantic import Field

from crewai.task import Task
from crewai.tasks.output_format import OutputFormat
from crewai.tasks.task_output import TaskOutput


class ConditionalTask(Task):
    """
    可根据另一个任务的输出有条件地执行的任务。
    注意：这不能是您团队中唯一的任务，也不能是第一个任务，因为它需要来自先前任务的上下文。
    """

    condition: Callable[[TaskOutput], bool] = Field(
        default=None,
        description="代理在发生错误时执行任务的最大重试次数。",
    )

    def __init__(
        self,
        condition: Callable[[Any], bool],
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.condition = condition

    def should_execute(self, context: TaskOutput) -> bool:
        """
        根据提供的上下文确定是否应执行条件任务。

        参数：
            context (Any)：将由条件评估的先前任务的上下文或输出。

        返回值：
            bool：如果应执行任务，则为 True，否则为 False。
        """
        return self.condition(context)

    def get_skipped_task_output(self):
        return TaskOutput(
            description=self.description,
            raw="",
            agent=self.agent.role if self.agent else "",
            output_format=OutputFormat.RAW,
        )
    