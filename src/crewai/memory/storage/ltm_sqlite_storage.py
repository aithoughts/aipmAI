import json
import sqlite3
from typing import Any, Dict, List, Optional, Union

from crewai.utilities import Printer
from crewai.utilities.paths import db_storage_path


class LTMSQLiteStorage:
    """
    用于 LTM 数据存储的更新版 SQLite 存储类。
    """

    def __init__(
        self, db_path: str = f"{db_storage_path()}/long_term_memory_storage.db"
    ) -> None:
        self.db_path = db_path
        self._printer: Printer = Printer()
        self._initialize_db()

    def _initialize_db(self):
        """
        初始化 SQLite 数据库并创建 LTM 表
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS long_term_memories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        task_description TEXT,
                        metadata TEXT,
                        datetime TEXT,
                        score REAL
                    )
                """
                )

                conn.commit()
        except sqlite3.Error as e:
            self._printer.print(
                content=f"内存错误：数据库初始化期间发生错误：{e}",
                color="red",
            )

    def save(
        self,
        task_description: str,
        metadata: Dict[str, Any],
        datetime: str,
        score: Union[int, float],
    ) -> None:
        """将数据保存到 LTM 表，并进行错误处理。"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                INSERT INTO long_term_memories (task_description, metadata, datetime, score)
                VALUES (?, ?, ?, ?)
            """,
                    (task_description, json.dumps(metadata), datetime, score),
                )
                conn.commit()
        except sqlite3.Error as e:
            self._printer.print(
                content=f"内存错误：保存到 LTM 时出错：{e}",
                color="red",
            )

    def load(
        self, task_description: str, latest_n: int
    ) -> Optional[List[Dict[str, Any]]]:
        """按任务描述查询 LTM 表，并进行错误处理。"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    f"""
                    SELECT metadata, datetime, score
                    FROM long_term_memories
                    WHERE task_description = ?
                    ORDER BY datetime DESC, score ASC
                    LIMIT {latest_n}
                """,
                    (task_description,),
                )
                rows = cursor.fetchall()
                if rows:
                    return [
                        {
                            "metadata": json.loads(row[0]),
                            "datetime": row[1],
                            "score": row[2],
                        }
                        for row in rows
                    ]

        except sqlite3.Error as e:
            self._printer.print(
                content=f"内存错误：查询 LTM 时出错：{e}",
                color="red",
            )
        return None

    def reset(
        self,
    ) -> None:
        """重置 LTM 表，并进行错误处理。"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM long_term_memories")
                conn.commit()

        except sqlite3.Error as e:
            self._printer.print(
                content=f"内存错误：删除 LTM 中的所有行时出错：{e}",
                color="red",
            )
        return None
