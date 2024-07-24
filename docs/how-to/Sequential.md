---
title: 在 crewAI 中使用顺序流程
description: 有关在 crewAI 项目中利用顺序流程执行任务的综合指南。
---

## 简介
CrewAI 提供了一个灵活的框架，用于以结构化的方式执行任务，支持顺序和分层流程。本指南概述了如何有效地实施这些流程，以确保高效的任务执行和项目完成。

## 顺序流程概述
顺序流程确保任务一个接一个地执行，遵循线性进程。这种方法适用于需要按特定顺序完成任务的项目。

### 主要特点
- **线性任务流**：通过按预定顺序处理任务来确保有序进行。
- **简单性**：最适合具有清晰、循序渐进的任务的项目。
- **易于监控**：便于轻松跟踪任务完成情况和项目进度。

## 实施顺序流程
要使用顺序流程，请组建您的团队并按需要执行的顺序定义任务。

```python
from crewai import Crew, Process, Agent, Task

# 定义您的代理
researcher = Agent(
  role='研究员',
  goal='进行基础研究',
  backstory='一位经验丰富的研究员，热衷于发现见解'
)
analyst = Agent(
  role='数据分析师',
  goal='分析研究结果',
  backstory='一位细致的分析师，善于发现规律'
)
writer = Agent(
  role='作家',
  goal='起草最终报告',
  backstory='一位熟练的作家，具有撰写引人入胜的叙述的天赋'
)

research_task = Task(description='收集相关数据...', agent=researcher, expected_output='原始数据')
analysis_task = Task(description='分析数据...', agent=analyst, expected_output='数据见解')
writing_task = Task(description='撰写报告...', agent=writer, expected_output='最终报告')

# 使用顺序流程组建团队
report_crew = Crew(
  agents=[researcher, analyst, writer],
  tasks=[research_task, analysis_task, writing_task],
  process=Process.sequential
)

# 执行团队
result = report_crew.kickoff()
```

### 工作流程实际应用
1. **初始任务**：在顺序流程中，第一个代理完成其任务并发出完成信号。
2. **后续任务**：代理根据流程类型选择其任务，并以先前任务的结果或经理指令指导其执行。
3. **完成**：最终任务执行完毕后，流程结束，从而完成项目。

## 高级功能

### 任务委派
在顺序流程中，如果代理的 `allow_delegation` 设置为 `True`，则他们可以将任务委派给团队中的其他代理。当团队中有多个代理时，将自动设置此功能。

### 异步执行
任务可以异步执行，从而在适当的时候允许并行处理。要创建异步任务，请在定义任务时设置 `async_execution=True`。

### 内存和缓存
CrewAI 支持内存和缓存功能：
- **内存**：在创建团队时设置 `memory=True` 来启用。这允许代理跨任务保留信息。
- **缓存**：默认情况下，缓存处于启用状态。设置 `cache=False` 以禁用它。

### 回调
您可以在任务和步骤级别设置回调：
- `task_callback`：在每次任务完成后执行。
- `step_callback`：在代理执行的每个步骤后执行。

### 使用指标
CrewAI 跟踪所有任务和代理的令牌使用情况。您可以在执行后访问这些指标。

## 顺序流程的最佳实践
1. **顺序至关重要**：按逻辑顺序排列任务，其中每个任务都建立在前一个任务的基础上。
2. **清晰的任务描述**：为每个任务提供详细的描述，以有效地指导代理。
3. **适当的代理选择**：使代理的技能和角色与每个任务的要求相匹配。
4. **使用上下文**：利用先前任务的上下文来通知后续任务
