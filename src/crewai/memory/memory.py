from typing import Any, Dict, Optional

from crewai.memory.storage.interface import Storage


class Memory:
    """
    memory的基类，现在支持代理标签和通用元数据。
    """

    def __init__(self, storage: Storage):
        self.storage = storage

    def save(
        self,
        value: Any,
        metadata: Optional[Dict[str, Any]] = None,
        agent: Optional[str] = None,
    ) -> None:
        metadata = metadata or {}
        if agent:
            metadata["agent"] = agent

        self.storage.save(value, metadata)  # type: ignore # 可能是一个 BUG？应该是 self.storage.save(key, value, metadata)

    def search(self, query: str) -> Dict[str, Any]:
        return self.storage.search(query)
