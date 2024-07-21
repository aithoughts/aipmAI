from typing import Any, Dict

from crewai.memory.long_term.long_term_memory_item import LongTermMemoryItem
from crewai.memory.memory import Memory
from crewai.memory.storage.ltm_sqlite_storage import LTMSQLiteStorage


class LongTermMemory(Memory):
    """
    长期记忆类，用于管理与整体 Crew 执行和性能相关的跨运行数据。
    继承自 Memory 类，并利用遵循 Storage 的类的实例进行数据存储，特别是处理 LongTermMemoryItem 实例。
    """

    def __init__(self):
        storage = LTMSQLiteStorage()
        super().__init__(storage)

    def save(self, item: LongTermMemoryItem) -> None:  # type: ignore # BUG?: “save” 的签名与超类型 “Memory” 不兼容
        metadata = item.metadata
        metadata.update({"agent": item.agent, "expected_output": item.expected_output})
        self.storage.save(  # type: ignore # BUG?: “Storage” 的 “save” 中没有名为 “task_description”、“score”、“datetime” 的参数
            task_description=item.task,
            score=metadata["quality"],
            metadata=metadata,
            datetime=item.datetime,
        )

    def search(self, task: str, latest_n: int = 3) -> Dict[str, Any]:
        return self.storage.load(task, latest_n)  # type: ignore # BUG?: “Storage” 没有 “load” 属性

    def reset(self) -> None:
        self.storage.reset()
