---
title: 条件任务
description: 了解如何在 crewAI 启动中使用条件任务
---

## 简介

crewAI 中的条件任务允许根据先前任务的结果动态调整工作流程。此强大功能使团队能够有选择地做出决策和执行任务，从而提高 AI 驱动流程的灵活性和效率。

```python
from typing import List

from pydantic import BaseModel
from crewai import Agent, Crew
from crewai.tasks.conditional_task import ConditionalTask
from crewai.tasks.task_output import TaskOutput
from crewai.task import Task
from crewai_tools import SerperDevTool


# 为条件任务定义条件函数
# 如果为 false，则跳过任务，如果为 true，则执行任务
def is_data_missing(output: TaskOutput) -> bool:
    return len(output.pydantic.events) < 10: # 这将跳过此任务

# 定义代理
data_fetcher_agent = Agent(
    role="数据获取器",
    goal="使用 Serper 工具在线获取数据",
    backstory="背景故事 1",
    verbose=True,
    tools=[SerperDevTool()],
)

data_processor_agent = Agent(
    role="数据处理器",
    goal="处理获取的数据",
    backstory="背景故事 2",
    verbose=True,
)

summary_generator_agent = Agent(
    role="摘要生成器",
    goal="从获取的数据生成摘要",
    backstory="背景故事 3",
    verbose=True,
)


class EventOutput(BaseModel):
    events: List[str]


task1 = Task(
    description="使用 Serper 工具获取有关旧金山事件的数据",
    expected_output="本周在旧金山要做的 10 件事的列表",
    agent=data_fetcher_agent,
    output_pydantic=EventOutput,
)

conditional_task = ConditionalTask(
    description="""
        检查数据是否缺失。如果我们的活动少于 10 个，
        则使用 Serper 工具获取更多活动，以便
        我们本周在旧金山总共有 10 个活动。
        """,
    expected_output="本周在旧金山要做的 10 件事的列表",
    condition=is_data_missing,
    agent=data_processor_agent,
)

task3 = Task(
    description="从获取的数据中生成旧金山事件的摘要",
    expected_output="summary_generated",
    agent=summary_generator_agent,
)

# 使用任务创建一个团队
crew = Crew(
    agents=[data_fetcher_agent, data_processor_agent, summary_generator_agent],
    tasks=[task1, conditional_task, task3],
    verbose=2,
)

result = crew.kickoff()
print("结果", result)
```
