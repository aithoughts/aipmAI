from enum import Enum


class Process(str, Enum):
    """
    表示可用于处理任务的不同流程的类。
    """

    sequential = "sequential"  # 顺序流程
    hierarchical = "hierarchical"  # 层级流程
    # TODO: consensual = 'consensual'  # 待办：共识流程
