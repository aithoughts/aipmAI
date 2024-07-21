from typing import Optional

from crewai.memory import EntityMemory, LongTermMemory, ShortTermMemory


class ContextualMemory:
    def __init__(self, stm: ShortTermMemory, ltm: LongTermMemory, em: EntityMemory):
        self.stm = stm
        self.ltm = ltm
        self.em = em

    def build_context_for_task(self, task, context) -> str:
        """
        自动为给定任务构建一组最小但高度相关的上下文信息。
        """
        query = f"{task.description} {context}".strip()

        if query == "":
            return ""

        context = []
        context.append(self._fetch_ltm_context(task.description))
        context.append(self._fetch_stm_context(query))
        context.append(self._fetch_entity_context(query))
        return "\n".join(filter(None, context))

    def _fetch_stm_context(self, query) -> str:
        """
        从 STM 中获取与任务描述和预期输出相关的最新见解，
        格式化为项目符号列表。
        """
        stm_results = self.stm.search(query)
        formatted_results = "\n".join([f"- {result}" for result in stm_results])
        return f"近期见解：\n{formatted_results}" if stm_results else ""

    def _fetch_ltm_context(self, task) -> Optional[str]:
        """
        从 LTM 中获取与任务描述和预期输出相关的历史数据或见解，
        格式化为项目符号列表。
        """
        ltm_results = self.ltm.search(task, latest_n=2)
        if not ltm_results:
            return None

        formatted_results = [
            suggestion
            for result in ltm_results
            for suggestion in result["metadata"]["suggestions"]  # type: ignore # 无效的索引类型 "str"，应该是 "SupportsIndex | slice"
        ]
        formatted_results = list(dict.fromkeys(formatted_results))
        formatted_results = "\n".join([f"- {result}" for result in formatted_results])  # type: ignore #  赋值类型不兼容（表达式类型为 "str"，变量类型为 "list[str]"）

        return f"历史数据：\n{formatted_results}" if ltm_results else ""

    def _fetch_entity_context(self, query) -> str:
        """
        从实体内存中获取与任务描述和预期输出相关的实体信息，
        格式化为项目符号列表。
        """
        em_results = self.em.search(query)
        formatted_results = "\n".join(
            [f"- {result['context']}" for result in em_results]  # type: ignore # 无效的索引类型 "str"，应该是 "SupportsIndex | slice"
        )
        return f"实体：\n{formatted_results}" if em_results else ""
