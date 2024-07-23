---
title: 在 CrewAI 中管理流程
description: 有关通过 CrewAI 中的流程进行工作流管理的详细指南，以及更新的实现细节。
---

## 理解流程
!!! note "核心概念"
    在 CrewAI 中，流程负责协调 agent 执行任务，类似于人类团队中的项目管理。这些流程确保任务按照预定义的策略高效地分配和执行。

## 流程实现

- **顺序**: 按顺序执行任务，确保任务按有序的进程完成。
- **分层**: 在管理层次结构中组织任务，其中任务根据结构化的指挥链进行委派和执行。必须在 crew 中指定管理者语言模型 (`manager_llm`) 或自定义管理者 agent (`manager_agent`) 才能启用分层流程，从而促进管理者创建和管理任务。
- **协商一致流程（计划中）**: 旨在让 agent 就任务执行进行协作决策，这种流程类型为 CrewAI 中的任务管理引入了一种民主的方法。它计划在未来开发，目前尚未在代码库中实现。

## 流程在团队合作中的作用
流程使各个 agent 能够作为一个有凝聚力的单元运作，简化他们的工作，以高效和一致的方式实现共同目标。

## 为 Crew 分配流程
要为 crew 分配流程，请在创建 crew 时指定流程类型以设置执行策略。对于分层流程，请确保为管理者 agent 定义 `manager_llm` 或 `manager_agent`。

```python
from crewai import Crew
from crewai.process import Process
from langchain_openai import ChatOpenAI

# 示例：使用顺序流程创建 crew
crew = Crew(
    agents=my_agents,
    tasks=my_tasks,
    process=Process.sequential
)

# 示例：使用分层流程创建 crew
# 确保提供 manager_llm 或 manager_agent
crew = Crew(
    agents=my_agents,
    tasks=my_tasks,
    process=Process.hierarchical,
    manager_llm=ChatOpenAI(model="gpt-4")
    # 或
    # manager_agent=my_manager_agent
)
```
**注意：** 确保在创建 `Crew` 对象之前定义了 `my_agents` 和 `my_tasks`，并且对于分层流程，还需要 `manager_llm` 或 `manager_agent`。

## 顺序流程
此方法反映了动态团队工作流程，以周到且系统的方式推进任务。任务执行遵循任务列表中预定义的顺序，一个任务的输出作为下一个任务的上下文。

要自定义任务上下文，请使用 `Task` 类中的 `context` 参数指定应作为后续任务上下文的输出。

## 分层流程
模拟公司层级结构，CrewAI 允许指定自定义管理者 agent 或自动创建一个，需要指定管理者语言模型 (`manager_llm`)。此 agent 监督任务执行，包括计划、委派和验证。任务不是预先分配的；管理者根据 agent 的能力分配任务，审查输出并评估任务完成情况。

## 流程类：详细概述
`Process` 类实现为枚举 (`Enum`)，确保类型安全并将流程值限制为定义的类型（`sequential`、`hierarchical`）。协商一致流程计划在未来纳入，强调我们对持续发展和创新的承诺。

## 其他任务功能
- **异步执行**: 现在可以异步执行任务，从而实现并行处理并提高效率。此功能旨在使任务能够同时执行，从而提高 crew 的整体效率。
- **人工输入审查**:  一项可选功能，支持人工审查任务输出，以确保最终确定之前的质量和准确性。此附加步骤引入了一层监督，为人工干预和验证提供了机会。
- **输出自定义**: 任务支持各种输出格式，包括 JSON (`output_json`)、Pydantic 模型 (`output_pydantic`) 和文件输出 (`output_file`)，从而在捕获和利用任务结果方面提供灵活性。这允许各种输出可能性，以满足不同的需求和要求。

## 结论
CrewAI 中的流程促进了结构化的协作，这对于实现 agent 之间的系统团队合作至关重要。本文档已更新，以反映最新功能、增强功能以及计划集成的协商一致流程，确保用户能够访问最新和最全面的信息。
