---
title: crewAI 任务
description: 详细介绍如何在 crewAI 框架内管理和创建任务，反映最新的代码库更新。
---

## 任务概述

!!! note "什么是任务？"
    在 crewAI 框架中，任务是由代理完成的特定分配。它们提供了执行所需的所有必要细节，例如描述、负责的代理、所需的工具等，从而简化了各种操作的复杂性。

crewAI 中的任务可以是协作式的，需要多个代理协同工作。这是通过任务属性进行管理，并由 Crew 的流程进行协调，从而提高了团队合作和效率。

## 任务属性

| 属性    | 参数    | 描述    |
| :---------------- | :---------------- | :---------------- |
| **描述** | `description` | 对任务内容的清晰简洁的陈述。   |
| **代理**   | `agent`   | 负责任务的代理，可以直接分配，也可以由团队流程决定。   |
| **预期输出**  | `expected_output` | 对任务完成情况的详细描述。    |
| **工具** _(可选)_   | `tools`   | 代理可以用来执行任务的功能或能力。    |
| **异步执行** _(可选)_ | `async_execution` | 如果设置了，则任务异步执行，允许在不等待完成的情况下继续进行。   |
| **上下文** _(可选)_ | `context` | 指定其输出用作此任务上下文的任务。    |
| **配置** _(可选)_  | `config`  | 用于执行任务的代理的其他配置详细信息，允许进一步自定义。    |
| **输出 JSON** _(可选)_ | `output_json` | 输出一个 JSON 对象，需要一个 OpenAI 客户端。只能设置一种输出格式。   |
| **输出 Pydantic** _(可选)_ | `output_pydantic` | 输出一个 Pydantic 模型对象，需要一个 OpenAI 客户端。只能设置一种输出格式。 |
| **输出文件** _(可选)_ | `output_file` | 将任务输出保存到文件。如果与 `Output JSON` 或 `Output Pydantic` 一起使用，则指定如何保存输出。 |
| **输出** _(可选)_  | `output`  | 任务的输出，包含原始、JSON 和 Pydantic 输出以及其他详细信息。   |
| **回调** _(可选)_    | `callback`    | 一个 Python 可调用对象，在任务完成后使用任务的输出执行。 |
| **人工输入** _(可选)_ | `human_input` | 指示任务是否需要在结束时进行人工反馈，这对于需要人工监督的任务很有用。 |

## 创建任务

创建任务涉及定义其范围、负责的代理以及任何额外的属性以提高灵活性：

```python
from crewai import Task

task = Task(
    description='查找并总结有关 AI 的最新和最相关的新闻',
    agent=sales_agent,
    expected_output='前 5 名最重要的 AI 新闻的项目符号列表摘要',
)
```

!!! note "任务分配"
直接指定要分配的 `agent`，或者让 `hierarchical` crewAI 的流程根据角色、可用性等来决定。

## 任务输出

!!! note "了解任务输出"
crewAI 框架中任务的输出封装在 `TaskOutput` 类中。此类提供了一种结构化方式来访问任务的结果，包括各种格式，例如原始字符串、JSON 和 Pydantic 模型。
默认情况下，`TaskOutput` 将仅包含 `raw` 输出。仅当原始 `Task` 对象配置了 `output_pydantic` 或 `output_json` 时，`TaskOutput` 才会分别包含 `pydantic` 或 `json_dict` 输出。

### 任务输出属性

| 属性 | 参数  | 类型  | 描述   |
| :---------------- | :-------------- | :-------------- | :-------------- |
| **描述**   | `description`   | `str` | 任务的简要描述。    |
| **摘要**   | `summary`   | `Optional[str]`    | 任务的简短摘要，从描述中自动生成。 |
| **原始**   | `raw`   | `str` | 任务的原始输出。这是输出的默认格式。    |
| **Pydantic**  | `pydantic`  | `Optional[BaseModel]`  | 表示任务结构化输出的 Pydantic 模型对象。   |
| **JSON 字典** | `json_dict` | `Optional[Dict[str, Any]]` | 表示任务 JSON 输出的字典。   |
| **代理** | `agent` | `str` | 执行任务的代理。   |
| **输出格式** | `output_format` | `OutputFormat` | 任务输出的格式，选项包括 RAW、JSON 和 Pydantic。默认为 RAW。 |

### 任务输出方法和属性

| 方法/属性 | 描述  |
| :-------------- | :-------------- |
| **json**    | 如果输出格式为 JSON，则返回任务输出的 JSON 字符串表示形式。   |
| **to_dict** | 将 JSON 和 Pydantic 输出转换为字典。 |
| **str** | 返回任务输出的字符串表示形式，优先级为 Pydantic，然后是 JSON，然后是原始。 |

### 访问任务输出

任务执行完成后，可以通过 `Task` 对象的 `output` 属性访问其输出。`TaskOutput` 类提供了多种与输出交互和呈现输出的方式。

#### 示例

```python
# 示例任务
task = Task(
    description='查找并总结最新的 AI 新闻',
    expected_output='前 5 名最重要的 AI 新闻的项目符号列表摘要',
    agent=research_agent,
    tools=[search_tool]
)

# 执行团队
crew = Crew(
    agents=[research_agent],
    tasks=[task],
    verbose=2
)

result = crew.kickoff()

# 访问任务输出
task_output = task.output

print(f"任务描述: {task_output.description}")
print(f"任务摘要: {task_output.summary}")
print(f"原始输出: {task_output.raw}")
if task_output.json_dict:
    print(f"JSON 输出: {json.dumps(task_output.json_dict, indent=2)}")
if task_output.pydantic:
    print(f"Pydantic 输出: {task_output.pydantic}")
```

## 将工具与任务集成

利用 [crewAI 工具包](https://github.com/aithoughts/aipmAI-tools) 和 [LangChain 工具](https://python.langchain.com/docs/integrations/tools) 中的工具来增强任务性能和代理交互。

## 使用工具创建任务

```python
import os
os.environ["OPENAI_API_KEY"] = "您的密钥"
os.environ["SERPER_API_KEY"] = "您的密钥" # serper.dev API 密钥

from crewai import Agent, Task, Crew
from crewai_tools import SerperDevTool

research_agent = Agent(
  role='研究员',
  goal='查找并总结最新的 AI 新闻',
  backstory="""您是一家大公司的研究员。
  您负责分析数据并为企业提供见解。""",
  verbose=True
)

search_tool = SerperDevTool()

task = Task(
  description='查找并总结最新的 AI 新闻',
  expected_output='前 5 名最重要的 AI 新闻的项目符号列表摘要',
  agent=research_agent,
  tools=[search_tool]
)

crew = Crew(
    agents=[research_agent],
    tasks=[task],
    verbose=2
)

result = crew.kickoff()
print(result)
```

这演示了如何使用特定工具的任务可以覆盖代理的默认设置，以进行定制的任务执行。

## 引用其他任务

在 crewAI 中，一个任务的输出会自动传递到下一个任务中，但您可以专门定义哪些任务的输出（包括多个任务）应该用作另一个任务的上下文。

当您有一个任务依赖于另一个不是紧随其后执行的任务的输出时，这很有用。这是通过任务的 `context` 属性完成的：

```python
# ...

research_ai_task = Task(
    description='查找并总结最新的 AI 新闻',
    expected_output='前 5 名最重要的 AI 新闻的项目符号列表摘要',
    async_execution=True,
    agent=research_agent,
    tools=[search_tool]
)

research_ops_task = Task(
    description='查找并总结最新的 AI Ops 新闻',
    expected_output='前 5 名最重要的 AI Ops 新闻的项目符号列表摘要',
    async_execution=True,
    agent=research_agent,
    tools=[search_tool]
)

write_blog_task = Task(
    description="撰写一篇关于 AI 的重要性及其最新新闻的完整博客文章",
    expected_output='4 段长的完整博客文章',
    agent=writer_agent,
    context=[research_ai_task, research_ops_task]
)

#...
```

## 异步执行

您可以将任务定义为异步执行。这意味着团队不会等待它完成就继续执行下一个任务。这对于需要很长时间才能完成的任务或对下一个要执行的任务不重要的任务很有用。

然后，您可以使用 `context` 属性在未来的任务中定义它应该等待异步任务的输出完成。

```python
#...

list_ideas = Task(
    description="列出 5 个关于 AI 文章的有趣想法。",
    expected_output="5 个文章想法的项目符号列表。",
    agent=researcher,
    async_execution=True # 将异步执行
)

list_important_history = Task(
    description="研究 AI 的历史，并告诉我 5 个最重要的事件。",
    expected_output="5 个重要事件的项目符号列表。",
    agent=researcher,
    async_execution=True # 将异步执行
)

write_article = Task(
    description="撰写一篇关于 AI 及其历史和有趣想法的文章。",
    expected_output="一篇关于 AI 的 4 段文章。",
    agent=writer,
    context=[list_ideas, list_important_history] # 将等待两个任务的输出完成
)

#...
```

## 回调机制

回调函数在任务完成后执行，允许根据任务的结果触发操作或通知。

```python
# ...

def callback_function(output: TaskOutput):
    # 任务完成后执行某些操作
    # 例如：向经理发送电子邮件
    print(f"""
        任务已完成！
        任务: {output.description}
        输出: {output.raw_output}
    """)

research_task = Task(
    description='查找并总结最新的 AI 新闻',
    expected_output='前 5 名最重要的 AI 新闻的项目符号列表摘要',
    agent=research_agent,
    tools=[search_tool],
    callback=callback_function
)

#...
```

## 访问特定任务输出

团队完成运行后，您可以使用任务对象的 `output` 属性访问特定任务的输出：

```python
# ...
task1 = Task(
    description='查找并总结最新的 AI 新闻',
    expected_output='前 5 名最重要的 AI 新闻的项目符号列表摘要',
    agent=research_agent,
    tools=[search_tool]
)

#...

crew = Crew(
    agents=[research_agent],
    tasks=[task1, task2, task3],
    verbose=2
)

result = crew.kickoff()

# 返回一个 TaskOutput 对象，其中包含任务的描述和结果
print(f"""
    任务已完成！
    任务: {task1.output.description}
    输出: {task1.output.raw_output}
""")
```

## 工具覆盖机制

在任务中指定工具允许动态调整代理功能，强调 CrewAI 的灵活性。

## 错误处理和验证机制

在创建和执行任务时，会采用某些验证机制来确保任务属性的健壮性和可靠性。这些机制包括但不限于：

- 确保每个任务只设置一种输出类型，以保持清晰的输出预期。
- 防止手动分配 `id` 属性，以维护唯一标识符系统的完整性。

这些验证有助于维护 crewAI 框架内任务执行的一致性和可靠性。

## 保存文件时创建目录

您现在可以指定任务在将其输出保存到文件时是否应创建目录。这对于组织输出和确保文件路径结构正确特别有用。

```python
# ...

save_output_task = Task(
    description='将汇总的 AI 新闻保存到文件',
    expected_output='文件保存成功',
    agent=research_agent,
    tools=[file_save_tool],
    output_file='outputs/ai_news_summary.txt',
    create_directory=True
)

#...
```

## 结论

任务是 crewAI 中代理行动的驱动力。通过正确定义任务及其结果，您为 AI 代理有效地独立工作或作为协作单元工作奠定了基础。为任务配备适当的工具、了解执行过程以及遵循可靠的验证实践对于最大限度地发挥 CrewAI 的潜力至关重要，确保代理为其分配的任务做好充分准备，并按预期执行任务。
