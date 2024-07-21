from crewai.memory.entity.entity_memory_item import EntityMemoryItem
from crewai.memory.memory import Memory
from crewai.memory.storage.rag_storage import RAGStorage


class EntityMemory(Memory):
    """
    EntityMemory 类，用于使用 SQLite 存储管理有关实体及其关系的结构化信息。
    继承自 Memory 类。
    """

    def __init__(self, crew=None, embedder_config=None):
        storage = RAGStorage(
            type="entities",
            allow_reset=False,
            embedder_config=embedder_config,
            crew=crew,
        )
        super().__init__(storage)

    def save(self, item: EntityMemoryItem) -> None:  # type: ignore # BUG?: “save” 的签名与超类型 “Memory” 不兼容
        """将实体项保存到 SQLite 存储中。"""
        data = f"{item.name}({item.type}): {item.description}"
        super().save(data, item.metadata)

    def reset(self) -> None:
        try:
            self.storage.reset()
        except Exception as e:
            raise Exception(f"重置实体memory时出错：{e}")
