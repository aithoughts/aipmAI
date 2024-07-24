---
title: 编码代理
description: 了解如何使您的 crewAI 代理能够编写和执行代码，并探索增强功能的高级功能。
---

## 简介

crewAI 代理现在拥有强大的编写和执行代码的能力，从而显著增强了其解决问题的能力。此功能对于需要计算或编程解决方案的任务特别有用。

## 启用代码执行

要为代理启用代码执行，请在创建代理时将 `allow_code_execution` 参数设置为 `True`。以下是一个示例：

```python
from crewai import Agent

coding_agent = Agent(
    role="高级 Python 开发人员",
    goal="编写设计良好且经过深思熟虑的代码",
    backstory="你是一位高级 Python 开发人员，在软件架构和最佳实践方面拥有丰富的经验。",
    allow_code_execution=True
)
```

## 重要注意事项

1. **模型选择**：强烈建议在启用代码执行时使用功能更强大的模型，例如 Claude 3.5 Sonnet 和 GPT-4。这些模型对编程概念有更好的理解，并且更有可能生成正确且高效的代码。

2. **错误处理**：代码执行功能包括错误处理。如果执行的代码引发异常，代理将收到错误消息，并且可以尝试更正代码或提供替代解决方案。

3. **依赖项**：要使用代码执行功能，您需要安装 `crewai_tools` 包。如果未安装，代理将记录一条信息消息：“编码工具不可用。请安装 crewai_tools。”

## 代码执行过程

当启用了代码执行的代理遇到需要编程的任务时：

1. 代理分析任务并确定需要执行代码。
2. 它编写解决问题所需的 Python 代码。
3. 代码被发送到内部代码执行工具（`CodeInterpreterTool`）。
4. 该工具在受控环境中执行代码并返回结果。
5. 代理解释结果并将其合并到其响应中，或将其用于进一步解决问题。

## 用法示例

以下是一个创建具有代码执行功能的代理并在任务中使用它的详细示例：

```python
from crewai import Agent, Task, Crew

# 创建启用了代码执行的代理
coding_agent = Agent(
    role="Python 数据分析师",
    goal="使用 Python 分析数据并提供见解",
    backstory="你是一位经验丰富的数据分析师，拥有强大的 Python 技能。",
    allow_code_execution=True
)

# 创建需要执行代码的任务
data_analysis_task = Task(
    description="分析给定的数据集并计算参与者的平均年龄。",
    agent=coding_agent
)

# 创建一个团队并添加任务
analysis_crew = Crew(
    agents=[coding_agent],
    tasks=[data_analysis_task]
)

# 执行团队
result = analysis_crew.kickoff()

print(result)
```

在此示例中，`coding_agent` 可以编写和执行 Python 代码来执行数据分析任务。
