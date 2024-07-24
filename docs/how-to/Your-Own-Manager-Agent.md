---
title: 在 CrewAI 中设置特定代理作为经理
description: 了解如何在 CrewAI 中设置自定义代理作为经理，从而更好地控制任务管理和协调。

---

# 在 CrewAI 中设置特定代理作为经理

CrewAI 允许用户设置特定代理作为团队的经理，从而更好地控制任务的管理和协调。此功能可以自定义管理角色，以更好地满足您的项目需求。

## 使用 `manager_agent` 属性

### 自定义经理代理

`manager_agent` 属性允许您定义一个自定义代理来管理团队。该代理将监督整个过程，确保高效、高质量地完成任务。

### 示例

```python
import os
from crewai import Agent, Task, Crew, Process

# 定义您的代理
researcher = Agent(
    role="研究员",
    goal="对 AI 和 AI 代理进行深入研究和分析",
    backstory="您是一位专家研究员，专门研究技术、软件工程、AI 和初创公司。您是一名自由职业者，目前正在为一位新客户进行研究。",
    allow_delegation=False,
)

writer = Agent(
    role="高级作家",
    goal="创建关于 AI 和 AI 代理的引人入胜的内容",
    backstory="您是一位高级作家，专门研究技术、软件工程、AI 和初创公司。您是一名自由职业者，目前正在为一位新客户撰写内容。",
    allow_delegation=False,
)

# 定义您的任务
task = Task(
    description="生成 5 个有趣的文章创意，然后为每个创意写一段引人入胜的段落，以展示该主题的完整文章的潜力。返回包含段落和注释的创意列表。",
    expected_output="5 个项目符号，每个项目符号都包含一个段落和相应的注释。",
)

# 定义经理代理
manager = Agent(
    role="项目经理",
    goal="高效管理团队并确保高质量地完成任务",
    backstory="您是一位经验丰富的项目经理，擅长监督复杂项目并引导团队取得成功。您的职责是协调团队成员的工作，确保每项任务都按时完成并达到最高标准。",
    allow_delegation=True,
)

# 使用自定义经理实例化您的团队
crew = Crew(
    agents=[researcher, writer],
    tasks=[task],
    manager_agent=manager,
    process=Process.hierarchical,
)

# 开始团队的工作
result = crew.kickoff()
```

## 自定义经理代理的优势

- **增强的控制力**：根据项目的特定需求定制管理方法。
- **改进的协调性**：确保由经验丰富的代理进行高效的任务协调和管理。
- **可定制的管理**：定义与项目目标一致的管理角色和职责。

## 设置经理 LLM

如果您正在使用分层流程并且不想设置自定义经理代理，则可以为经理指定语言模型：

```python
from langchain_openai import ChatOpenAI

manager_llm = ChatOpenAI(model_name="gpt-4")

crew = Crew(
    agents=[researcher, writer],
    tasks=[task],
    process=Process.hierarchical,
    manager_llm=manager_llm
)
```

注意：使用分层流程时，必须设置 `manager_agent` 或 `manager_llm`。
