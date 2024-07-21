from crewai.memory.memory import Memory
from crewai.memory.short_term.short_term_memory_item import ShortTermMemoryItem
from crewai.memory.storage.rag_storage import RAGStorage


class ShortTermMemory(Memory):
    """
    短期记忆类，用于管理与当前任务和交互相关的瞬态数据。
    继承自 Memory 类，并利用遵循 Storage 的类的实例进行数据存储，特别是处理 MemoryItem 实例。
    """

    def __init__(self, crew=None, embedder_config=None):
        storage = RAGStorage(
            type="short_term", embedder_config=embedder_config, crew=crew
        )
        super().__init__(storage)

    def save(self, item: ShortTermMemoryItem) -> None:
        super().save(item.data, item.metadata, item.agent)

    def search(self, query: str, score_threshold: float = 0.35):
        return self.storage.search(query=query, score_threshold=score_threshold)  # type: ignore # BUG？引用的是父类，但父类没有这些参数

    def reset(self) -> None:
        try:
            self.storage.reset()
        except Exception as e:
            raise Exception(f"重置短期记忆时出错：{e}")
