from typing import Any, Dict


class Storage:
    """定义存储接口的抽象基类"""

    def save(self, key: str, value: Any, metadata: Dict[str, Any]) -> None:
        pass

    def search(self, key: str) -> Dict[str, Any]:  # type: ignore
        pass

    def reset(self) -> None:
        pass
