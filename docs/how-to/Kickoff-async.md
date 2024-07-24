---
title: 异步启动
description: 异步启动 Crew
---

## 简介
CrewAI 提供了异步启动 Crew 的能力，允许您以非阻塞的方式启动 Crew 执行。当您希望同时运行多个 Crew 或在 Crew 执行时需要执行其他任务时，此功能特别有用。

## 异步 Crew 执行
要异步启动 Crew，请使用 `kickoff_async()` 方法。此方法在一个单独的线程中启动 Crew 执行，允许主线程继续执行其他任务。

以下是如何异步启动 Crew 的示例：

```python
from crewai import Crew, Agent, Task

# 创建启用了代码执行的代理
coding_agent = Agent(
    role="Python 数据分析师",
    goal="使用 Python 分析数据并提供见解",
    backstory="你是一位经验丰富的数据分析师，拥有强大的 Python 技能。",
    allow_code_execution=True
)

# 创建需要执行代码的任务
data_analysis_task = Task(
    description="分析给定的数据集并计算参与者的平均年龄。年龄：{ages}",
    agent=coding_agent
)

# 创建一个团队并添加任务
analysis_crew = Crew(
    agents=[coding_agent],
    tasks=[data_analysis_task]
)

# 执行团队
result = analysis_crew.kickoff_async(inputs={"ages": [25, 30, 35, 40, 45]})
```
