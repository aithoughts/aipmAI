---
title: 为每个项目启动
description: 为列表中的每个项目启动 Crew
---

## 简介
CrewAI 提供了为列表中的每个项目启动 Crew 的能力，允许您为列表中的每个项目执行 Crew。当您需要对多个项目执行相同的任务集时，此功能特别有用。

## 为每个项目启动 Crew
要为列表中的每个项目启动 Crew，请使用 `kickoff_for_each()` 方法。此方法将为列表中的每个项目执行 Crew，从而允许您高效地处理多个项目。

以下是如何为列表中的每个项目启动 Crew 的示例：

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

datasets = [
  { "ages": [25, 30, 35, 40, 45] },
  { "ages": [20, 25, 30, 35, 40] },
  { "ages": [30, 35, 40, 45, 50] }
]

# 执行团队
result = analysis_crew.kickoff_for_each(inputs=datasets)
```
