from typing import Any, Dict, List

import tiktoken
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import LLMResult

from crewai.agents.agent_builder.utilities.base_token_process import TokenProcess


class TokenCalcHandler(BaseCallbackHandler):
    """
    用于计算 Token 使用量的回调处理器。
    """

    model_name: str = ""  # 模型名称
    token_cost_process: TokenProcess  # Token 使用量处理对象

    def __init__(self, model_name, token_cost_process):
        """
        初始化 TokenCalcHandler。

        :param model_name: 模型名称。
        :param token_cost_process: Token 使用量处理对象。
        """
        self.model_name = model_name
        self.token_cost_process = token_cost_process

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """
        在 LLM 开始处理请求时调用。

        :param serialized: 序列化后的 LLM 对象。
        :param prompts: 提示列表。
        :param kwargs: 其他参数。
        """
        try:
            encoding = tiktoken.encoding_for_model(self.model_name)  # 获取模型对应的编码器
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")  # 如果没有找到对应的编码器，则使用默认编码器

        if self.token_cost_process is None:
            return

        for prompt in prompts:
            self.token_cost_process.sum_prompt_tokens(
                len(encoding.encode(prompt))
            )  # 计算并累加提示的 Token 数量

    async def on_llm_new_token(self, token: str, **kwargs) -> None:
        """
        在 LLM 生成新 Token 时调用。

        :param token: 新生成的 Token。
        :param kwargs: 其他参数。
        """
        self.token_cost_process.sum_completion_tokens(1)  # 累加完成 Token 数量

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """
        在 LLM 完成请求处理时调用。

        :param response: LLM 的响应结果。
        :param kwargs: 其他参数。
        """
        self.token_cost_process.sum_successful_requests(1)  # 累加成功请求数量
