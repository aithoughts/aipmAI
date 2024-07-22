from typing import List

from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from crewai.utilities import Converter
from crewai.utilities.pydantic_schema_parser import PydanticSchemaParser

agentops = None
try:
    from agentops import track_agent
except ImportError:

    def track_agent(name):
        def noop(f):
            return f

        return noop


class Entity(BaseModel):
    """实体"""
    name: str = Field(description="实体名称")
    type: str = Field(description="实体类型")
    description: str = Field(description="实体描述")
    relationships: List[str] = Field(description="实体关系")


class TaskEvaluation(BaseModel):
    """任务评估"""
    suggestions: List[str] = Field(
        description="对未来类似任务改进的建议"
    )
    quality: float = Field(
        description="从 0 到 10 的评分，根据任务描述、预期输出和任务结果，评估完成度、质量和整体性能"
    )
    entities: List[Entity] = Field(
        description="从任务输出中提取的实体"
    )


class TrainingTaskEvaluation(BaseModel):
    """训练任务评估"""
    suggestions: List[str] = Field(
        description="根据人工反馈以及初始输出和改进输出之间的比较，提供基于人工反馈的未来任务行动项"
    )
    quality: float = Field(
        description="从 0 到 10 的评分，根据人工反馈，从改进输出到初始输出，评估完成度、质量和整体性能"
    )
    final_summary: str = Field(
        description="基于人工反馈和改进输出，逐步改进下一个代理的行动项"
    )


@track_agent(name="任务评估器")
class TaskEvaluator:
    def __init__(self, original_agent):
        self.llm = original_agent.llm

    def evaluate(self, task, ouput) -> TaskEvaluation:
        """评估任务"""
        evaluation_query = (
            f"根据描述、预期输出和实际结果评估已完成任务的质量。\n\n"
            f"任务描述：\n{task.description}\n\n"
            f"预期输出：\n{task.expected_output}\n\n"
            f"实际输出：\n{ouput}\n\n"
            "请提供：\n"
            "- 改进未来类似任务的建议要点\n"
            "- 从 0 到 10 的评分，评估完成度、质量和整体性能\n"
            "- 从任务输出中提取的实体（如果有），包括其类型、描述和关系"
        )

        instructions = "我将把这段原始文本转换为有效的 JSON。"

        if not self._is_gpt(self.llm):
            model_schema = PydanticSchemaParser(model=TaskEvaluation).get_schema()
            instructions = f"{instructions}\n\nJSON 应具有以下结构，并包含以下键：\n{model_schema}"

        converter = Converter(
            llm=self.llm,
            text=evaluation_query,
            model=TaskEvaluation,
            instructions=instructions,
        )

        return converter.to_pydantic()

    def _is_gpt(self, llm) -> bool:
        return isinstance(llm, ChatOpenAI) and llm.openai_api_base is None

    def evaluate_training_data(
        self, training_data: dict, agent_id: str
    ) -> TrainingTaskEvaluation:
        """
        根据 llm 输出、人工反馈和改进后的输出评估训练数据。

        参数：
            - training_data (dict): 要评估的训练数据。
            - agent_id (str): 代理的 ID。
        """

        output_training_data = training_data[agent_id]

        final_aggregated_data = ""
        for _, data in output_training_data.items():
            final_aggregated_data += (
                f"初始输出：\n{data['initial_output']}\n\n"
                f"人工反馈：\n{data['human_feedback']}\n\n"
                f"改进后的输出：\n{data['improved_output']}\n\n"
            )

        evaluation_query = (
            "根据 llm 输出、人工反馈和 llm 输出改进结果评估训练数据的质量。\n\n"
            f"{final_aggregated_data}"
            "请提供：\n"
            "- 根据人工反馈以及初始输出和改进输出之间的比较，提供基于人工反馈的未来任务行动项\n"
            "- 从 0 到 10 的评分，根据人工反馈，从改进输出到初始输出，评估完成度、质量和整体性能\n"
        )
        instructions = "我将把这段原始文本转换为有效的 JSON。"

        if not self._is_gpt(self.llm):
            model_schema = PydanticSchemaParser(
                model=TrainingTaskEvaluation
            ).get_schema()
            instructions = f"{instructions}\n\nJSON 应具有以下结构，并包含以下键：\n{model_schema}"

        converter = Converter(
            llm=self.llm,
            text=evaluation_query,
            model=TrainingTaskEvaluation,
            instructions=instructions,
        )

        pydantic_result = converter.to_pydantic()
        return pydantic_result
