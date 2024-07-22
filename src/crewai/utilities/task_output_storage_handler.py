from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, Any, Optional, List
from crewai.memory.storage.kickoff_task_outputs_storage import (
    KickoffTaskOutputsSQLiteStorage,
)
from crewai.task import Task


class ExecutionLog(BaseModel):
    """
    存储任务执行日志的类。
    """

    task_id: str  # 任务 ID
    expected_output: Optional[str] = None  # 预期输出
    output: Dict[str, Any]  # 实际输出
    timestamp: datetime = Field(default_factory=datetime.now)  # 执行时间戳
    task_index: int  # 任务索引
    inputs: Dict[str, Any] = Field(default_factory=dict)  # 任务输入
    was_replayed: bool = False  # 是否为重放的任务

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)


class TaskOutputStorageHandler:
    """
    处理任务输出存储的类。
    """

    def __init__(self) -> None:
        """
        初始化 TaskOutputStorageHandler，使用 KickoffTaskOutputsSQLiteStorage 存储数据。
        """
        self.storage = KickoffTaskOutputsSQLiteStorage()

    def update(self, task_index: int, log: Dict[str, Any]):
        """
        更新指定索引的任务日志。

        :param task_index: 要更新的任务索引。
        :param log: 包含更新数据的日志字典。
        """
        saved_outputs = self.load()
        if saved_outputs is None:
            raise ValueError("日志不能为空。")

        if log.get("was_replayed", False):
            replayed = {
                "task_id": str(log["task"].id),
                "expected_output": log["task"].expected_output,
                "output": log["output"],
                "was_replayed": log["was_replayed"],
                "inputs": log["inputs"],
            }
            self.storage.update(
                task_index,
                **replayed,
            )
        else:
            self.storage.add(**log)

    def add(
        self,
        task: Task,
        output: Dict[str, Any],
        task_index: int,
        inputs: Dict[str, Any] = {},
        was_replayed: bool = False,
    ):
        """
        添加新的任务日志。

        :param task: 任务对象。
        :param output: 任务输出。
        :param task_index: 任务索引。
        :param inputs: 任务输入。
        :param was_replayed: 是否为重放的任务。
        """
        self.storage.add(task, output, task_index, was_replayed, inputs)

    def reset(self):
        """
        重置存储，删除所有日志。
        """
        self.storage.delete_all()

    def load(self) -> Optional[List[Dict[str, Any]]]:
        """
        加载所有保存的日志。

        :return: 包含所有日志的列表，如果没有任何日志则返回 None。
        """
        return self.storage.load()
