---
title: CrewAI 初步支持自带提示
description: 通过允许用户在 CrewAI 中自带提示来增强定制化和国际化。

---

# CrewAI 初步支持自带提示

CrewAI 现在支持自带提示功能，可实现广泛的定制化和国际化。此功能允许用户定制其代理的内部工作机制，以更好地满足特定需求，包括对多语言的支持。

## 国际化和定制化支持

### 使用 `prompt_file` 自定义提示

`prompt_file` 属性有助于完全自定义代理提示，从而增强 CrewAI 的全球可用性。用户可以指定他们的提示模板，确保代理以符合特定项目要求或语言偏好的方式进行沟通。

#### 自定义提示文件示例

自定义提示可以在 JSON 文件中定义，类似于 [此处](https://github.com/aithoughts/aipmAI/blob/main/src/crewai/translations/en.json) 提供的示例。

### 支持的语言

CrewAI 的自定义提示支持包括国际化，允许以不同语言编写提示。这对于需要多语言支持的全球团队或项目特别有用。

## 如何使用 `prompt_file` 属性

要使用 `prompt_file` 属性，请将其包含在您的 Crew 定义中。以下示例演示了如何使用自定义提示设置代理和任务。

### 示例

```python
import os
from crewai import Agent, Task, Crew

# 定义您的代理
researcher = Agent(
    role="Researcher",
    goal="对有关人工智能和人工智能代理的内容进行最佳研究和分析",
    backstory="您是一位专家研究员，专门研究技术、软件工程、人工智能和初创公司。您作为自由职业者工作，现在正在为新客户进行研究和分析。",
    allow_delegation=False,
)

writer = Agent(
    role="Senior Writer",
    goal="撰写有关人工智能和人工智能代理的最佳内容。",
    backstory="您是一位高级作家，专门研究技术、软件工程、人工智能和初创公司。您作为自由职业者工作，现在正在为新客户撰写内容。",
    allow_delegation=False,
)

# 定义您的任务
tasks = [
    Task(
        description="打招呼",
        expected_output="词语：你好",
        agent=researcher,
    )
]

# 使用自定义提示实例化您的 Crew
crew = Crew(
    agents=[researcher],
    tasks=tasks,
    prompt_file="prompt.json",  # 自定义提示文件的路径
)

# 让您的 Crew 开始工作！
crew.kickoff()
```

## 高级定制功能

### `language` 属性

除了 `prompt_file` 之外，还可以使用 `language` 属性指定代理提示的语言。这确保以所需的语言生成提示，进一步增强 CrewAI 的国际化能力。

### 创建自定义提示文件

自定义提示文件应采用 JSON 格式，并包含所有必要的提示模板。以下是提示 JSON 文件的简化示例：

```json
{
    "system": "您是一个系统模板。",
    "prompt": "这是您的提示模板。",
    "response": "这是您的响应模板。"
}
```

### 自定义提示的优势

- **增强的灵活性**: 根据特定项目需求定制代理沟通。
- **改进的可用性**: 支持多种语言，使其适用于全球项目。
- **一致性**: 确保不同代理和任务之间提示结构的统一性。

通过整合这些更新，CrewAI 为用户提供了完全自定义和国际化其代理提示的功能，使平台更加通用和用户友好。
