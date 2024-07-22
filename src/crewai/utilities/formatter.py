from typing import List

from crewai.task import Task
from crewai.tasks.task_output import TaskOutput


def aggregate_raw_outputs_from_task_outputs(task_outputs: List[TaskOutput]) -> str:
    """从任务输出中生成字符串上下文。"""
    dividers = "\n\n----------\n\n"  # 分隔符

    # 使用分隔符连接任务输出
    context = dividers.join(output.raw for output in task_outputs)
    return context


def aggregate_raw_outputs_from_tasks(tasks: List[Task]) -> str:
    """从任务中生成字符串上下文。"""
    task_outputs = [task.output for task in tasks if task.output is not None]  # 获取所有非空的任务输出

    return aggregate_raw_outputs_from_task_outputs(task_outputs)  # 使用 task_outputs 生成上下文
