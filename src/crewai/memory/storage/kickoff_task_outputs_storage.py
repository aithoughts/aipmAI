import json
import sqlite3
from typing import Any, Dict, List, Optional

from crewai.task import Task
from crewai.utilities import Printer
from crewai.utilities.crew_json_encoder import CrewJSONEncoder
from crewai.utilities.paths import db_storage_path


class KickoffTaskOutputsSQLiteStorage:
    """
    用于存储启动任务输出的更新版 SQLite 存储类。
    """

    def __init__(
        self, db_path: str = f"{db_storage_path()}/latest_kickoff_task_outputs.db"
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
                    CREATE TABLE IF NOT EXISTS latest_kickoff_task_outputs (
                        task_id TEXT PRIMARY KEY,
                        expected_output TEXT,
                        output JSON,
                        task_index INTEGER,
                        inputs JSON,
                        was_replayed BOOLEAN,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )

                conn.commit()
        except sqlite3.Error as e:
            self._printer.print(
                content=f"保存启动任务输出错误：数据库初始化期间发生错误：{e}",
                color="red",
            )

    def add(
        self,
        task: Task,
        output: Dict[str, Any],
        task_index: int,
        was_replayed: bool = False,
        inputs: Dict[str, Any] = {},
    ):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                INSERT OR REPLACE INTO latest_kickoff_task_outputs
                (task_id, expected_output, output, task_index, inputs, was_replayed)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                    (
                        str(task.id),
                        task.expected_output,
                        json.dumps(output, cls=CrewJSONEncoder),
                        task_index,
                        json.dumps(inputs),
                        was_replayed,
                    ),
                )
                conn.commit()
        except sqlite3.Error as e:
            self._printer.print(
                content=f"保存启动任务输出错误：数据库初始化期间发生错误：{e}",
                color="red",
            )

    def update(
        self,
        task_index: int,
        **kwargs,
    ):
        """
        根据 task_index 更新 latest_kickoff_task_outputs 表中的现有行。
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                fields = []
                values = []
                for key, value in kwargs.items():
                    fields.append(f"{key} = ?")
                    values.append(
                        json.dumps(value, cls=CrewJSONEncoder)
                        if isinstance(value, dict)
                        else value
                    )

                query = f"UPDATE latest_kickoff_task_outputs SET {', '.join(fields)} WHERE task_index = ?"
                values.append(task_index)

                cursor.execute(query, tuple(values))
                conn.commit()

                if cursor.rowcount == 0:
                    self._printer.print(
                        f"找不到 task_index 为 {task_index} 的行。未执行更新。",
                        color="red",
                    )
        except sqlite3.Error as e:
            self._printer.print(f"更新启动任务输出错误：{e}", color="red")

    def load(self) -> Optional[List[Dict[str, Any]]]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                SELECT *
                FROM latest_kickoff_task_outputs
                ORDER BY task_index
                """)

                rows = cursor.fetchall()
                results = []
                for row in rows:
                    result = {
                        "task_id": row[0],
                        "expected_output": row[1],
                        "output": json.loads(row[2]),
                        "task_index": row[3],
                        "inputs": json.loads(row[4]),
                        "was_replayed": row[5],
                        "timestamp": row[6],
                    }
                    results.append(result)

                return results

        except sqlite3.Error as e:
            self._printer.print(
                content=f"加载启动任务输出错误：查询启动任务输出时出错：{e}",
                color="red",
            )
            return None

    def delete_all(self):
        """
        删除 latest_kickoff_task_outputs 表中的所有行。
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM latest_kickoff_task_outputs")
                conn.commit()
        except sqlite3.Error as e:
            self._printer.print(
                content=f"错误：删除所有启动任务输出失败：{e}",
                color="red",
            )
