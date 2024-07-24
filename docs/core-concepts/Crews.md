---
title: crewAI Crews
description: 了解和利用 crewAI 框架中的 crew，包括全面的属性和功能。
---

## 什么是 Crew？

crewAI 中的 crew 表示一组协作的 agent，它们共同努力完成一组任务。每个 crew 都定义了任务执行策略、agent 协作和整体工作流程。

## Crew 属性

| 属性     | 参数 | 描述  |
| :--------------------- | :--------------------- | :--------------------- |
| **任务**     | `tasks`    | 分配给 crew 的任务列表。    |
| **Agent**    | `agents`   | 属于 crew 的 agent 列表。 |
| **流程** _(可选)_  | `process`  | crew 遵循的流程（例如，顺序、分层）。 |
| **详细** _(可选)_  | `verbose`  | 执行期间记录的详细程度。    |
| **管理者 LLM** _(可选)_ | `manager_llm` | 分层流程中管理者 agent 使用的语言模型。**使用分层流程时必填。** |
| **函数调用 LLM** _(可选)_ | `function_calling_llm` | 如果传递，crew 将使用此 LLM 为 crew 中所有 agent 的工具执行函数调用。每个 agent 可以有自己的 LLM，它会覆盖 crew 的 LLM 用于函数调用。 |
| **配置** _(可选)_   | `config`   | crew 的可选配置设置，采用 `Json` 或 `Dict[str, Any]` 格式。      |
| **最大 RPM** _(可选)_  | `max_rpm`  | crew 在执行期间遵守的每分钟最大请求数。   |
| **语言** _(可选)_ | `language` | crew 使用的语言，默认为英语。     |
| **语言文件** _(可选)_        | `language_file`        | 用于 crew 的语言文件的路径。   |
| **内存** _(可选)_   | `memory`   | 用于存储执行记忆（短期、长期、实体记忆）。 |
| **缓存** _(可选)_    | `cache`    | 指定是否使用缓存来存储工具执行的结果。   |
| **嵌入器** _(可选)_ | `embedder` | crew 使用的嵌入器的配置。目前主要由内存使用。    |
| **完整输出** _(可选)_ | `full_output` | crew 是否应返回包含所有任务输出的完整输出，还是仅返回最终输出。      |
| **步骤回调** _(可选)_        | `step_callback`        | 每个 agent 每一步之后调用的函数。这可用于记录 agent 的操作或执行其他操作；它不会覆盖特定于 agent 的 `step_callback`。     |
| **任务回调** _(可选)_        | `task_callback`        | 每个任务完成后调用的函数。用于在任务执行后进行监控或其他操作。    |
| **共享 Crew** _(可选)_  | `share_crew`  | 您是否希望与 crewAI 团队共享完整的 crew 信息和执行情况，以使库变得更好，并允许我们训练模型。        |
| **输出日志文件** _(可选)_      | `output_log_file`      | 您是否希望有一个包含完整 crew 输出和执行情况的文件。您可以使用 True 进行设置，它将默认为您当前所在的文件夹，并将被称为 logs.txt，或者传递一个包含文件完整路径和名称的字符串。 |
| **管理者 Agent** _(可选)_        | `manager_agent`        | `manager` 设置一个自定义 agent，它将用作管理者。    |
| **管理者回调** _(可选)_    | `manager_callbacks`    | `manager_callbacks` 接收一个回调处理程序列表，当使用分层流程时，管理者 agent 将执行这些处理程序。  |
| **提示文件** _(可选)_ | `prompt_file` | 用于 crew 的提示 JSON 文件的路径。     |
| **计划** *(可选)* | `planning` | 为 Crew 添加计划能力。当在每次 Crew 迭代之前激活时，所有 Crew 数据都会发送到 AgentPlanner，该 AgentPlanner 将计划任务，并且此计划将添加到每个任务描述中。

!!! note "Crew 最大 RPM"
`max_rpm` 属性设置 crew 每分钟可以执行的最大请求数，以避免速率限制，并且如果您设置了它，它将覆盖各个 agent 的 `max_rpm` 设置。

## 创建 Crew

组建 crew 时，您需要将具有互补角色和工具的 agent 组合起来，分配任务，并选择一个流程来规定它们的执行顺序和交互方式。

### 示例：组建 Crew

```python
from crewai import Crew, Agent, Task, Process
from langchain_community.tools import DuckDuckGoSearchRun
from crewai_tools import tool

@tool('DuckDuckGoSearch')
def search(search_query: str):
    """在网络上搜索有关给定主题的信息"""
    return DuckDuckGoSearchRun().run(search_query)

# 定义具有特定角色和工具的 agent
researcher = Agent(
    role='高级研究分析师',
    goal='发现创新的 AI 技术',
    backstory="""您是一家大公司的高级研究分析师。
        您负责分析数据并为企业提供见解。
        您目前正在开展一个项目，以分析人工智能领域的趋势和创新。""",
    tools=[search]
)

writer = Agent(
    role='内容撰稿人',
    goal='撰写有关 AI 发现的引人入胜的文章',
    backstory="""您是一家大公司的高级作家。
        您负责为企业创建内容。
        您目前正在开展一个项目，为您的下次会议撰写有关 AI 领域趋势和创新的文章。""",
    verbose=True
)

# 为 agent 创建任务
research_task = Task(
    description='识别突破性 AI 技术',
    agent=researcher,
    expected_output='前 5 名最重要的 AI 新闻的项目符号列表摘要'
)
write_article_task = Task(
    description='撰写一篇关于最新 AI 技术的文章',
    agent=writer,
    expected_output='关于最新 AI 技术的 3 段博客文章'
)

# 使用顺序流程组建 crew
my_crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, write_article_task],
    process=Process.sequential,
    full_output=True,
    verbose=True,
)
```

## Crew 输出

!!! note "了解 Crew 输出"
crewAI 框架中 crew 的输出封装在 `CrewOutput` 类中。
此类提供了一种结构化的方法来访问 crew 执行的结果，包括各种格式，如原始字符串、JSON 和 Pydantic 模型。
`CrewOutput` 包括最终任务输出的结果、token 使用情况和各个任务输出。

### Crew 输出属性

| 属性        | 参数     | 类型  | 描述      |
| :--------------------- | :--------------------- | :--------------------- | :--------------------- |
| **原始** | `raw` | `str` | crew 的原始输出。这是输出的默认格式。       |
| **Pydantic**     | `pydantic`     | `Optional[BaseModel]`      | 表示 crew 结构化输出的 Pydantic 模型对象。      |
| **JSON 字典**    | `json_dict`    | `Optional[Dict[str, Any]]` | 表示 crew JSON 输出的字典。  |
| **任务输出** | `tasks_output` | `List[TaskOutput]`         | `TaskOutput` 对象列表，每个对象表示 crew 中一个任务的输出。      |
| **Token 使用情况**  | `token_usage`  | `Dict[str, Any]`  | token 使用情况摘要，提供有关语言模型在执行期间性能的见解。 |

### Crew 输出方法和属性

| 方法/属性 | 描述   |
| :-------------- | :--------------------- |
| **json**        | 如果输出格式为 JSON，则返回 crew 输出的 JSON 字符串表示形式。  |
| **to_dict**     | 将 JSON 和 Pydantic 输出转换为字典。       |
| \***\*str\*\*** | 返回 crew 输出的字符串表示形式，优先级为 Pydantic，然后是 JSON，然后是原始。 |

### 访问 Crew 输出

执行 crew 后，可以通过 `Crew` 对象的 `output` 属性访问其输出。`CrewOutput` 类提供了各种方法来与该输出进行交互和呈现。

#### 示例

```python
# 示例 crew 执行
crew = Crew(
    agents=[research_agent, writer_agent],
    tasks=[research_task, write_article_task],
    verbose=2
)

result = crew.kickoff()

# 访问 crew 输出
print(f"原始输出：{crew_output.raw}")
if crew_output.json_dict:
    print(f"JSON 输出：{json.dumps(crew_output.json_dict, indent=2)}")
if crew_output.pydantic:
    print(f"Pydantic 输出：{crew_output.pydantic}")
print(f"任务输出：{crew_output.tasks_output}")
print(f"Token 使用情况：{crew_output.token_usage}")
```

## 内存利用

Crew 可以利用内存（短期、长期和实体内存）来增强其执行和学习能力。此功能允许 crew 存储和调用执行记忆，帮助制定决策和任务执行策略。

## 缓存利用

缓存可用于存储工具执行的结果，通过减少重新执行相同任务的需求，使流程更高效。

## Crew 使用指标

在 crew 执行之后，您可以访问 `usage_metrics` 属性以查看 crew 执行的所有任务的语言模型 (LLM) 使用指标。这提供了对运营效率和需要改进的领域的洞察。

```python
# 访问 crew 的使用指标
crew = Crew(agents=[agent1, agent2], tasks=[task1, task2])
crew.kickoff()
print(crew.usage_metrics)
```

## Crew 执行流程

- **顺序流程**: 任务一个接一个地执行，允许线性工作流程。
- **分层流程**: 管理者 agent 协调 crew，委派任务并在继续之前验证结果。**注意**: 此流程需要 `manager_llm` 或 `manager_agent`，并且对于验证流程至关重要。

### 启动 Crew

组建好 crew 后，使用 `kickoff()` 方法启动工作流程。这将根据定义的流程启动执行过程。

```python
# 启动 crew 的任务执行
result = my_crew.kickoff()
print(result)
```

### 启动 Crew 的不同方式

组建好 crew 后，使用相应的启动方法启动工作流程。CrewAI 提供了几种方法来更好地控制启动过程：`kickoff()`、`kickoff_for_each()`、`kickoff_async()` 和 `kickoff_for_each_async()`。

`kickoff()`: 根据定义的流程启动执行过程。
`kickoff_for_each()`: 单独为每个 agent 执行任务。
`kickoff_async()`: 异步启动工作流程。
`kickoff_for_each_async()`: 以异步方式单独为每个 agent 执行任务。

```python
# 启动 crew 的任务执行
result = my_crew.kickoff()
print(result)

# 使用 kickoff_for_each 的示例
inputs_array = [{'topic': '医疗保健中的 AI'}, {'topic': '金融中的 AI'}]
results = my_crew.kickoff_for_each(inputs=inputs_array)
for result in results:
    print(result)

# 使用 kickoff_async 的示例
inputs = {'topic': '医疗保健中的 AI'}
async_result = my_crew.kickoff_async(inputs=inputs)
print(async_result)

# 使用 kickoff_for_each_async 的示例
inputs_array = [{'topic': '医疗保健中的 AI'}, {'topic': '金融中的 AI'}]
async_results = my_crew.kickoff_for_each_async(inputs=inputs_array)
for async_result in async_results:
    print(async_result)
```

这些方法为管理和执行 crew 中的任务提供了灵活性，允许根据您的需求定制同步和异步工作流程。


### 从特定任务重放：
您现在可以使用我们的 cli 命令 replay 从特定任务重放。

CrewAI 中的重放功能允许您使用命令行界面 (CLI) 从特定任务开始重放。通过运行命令 `crewai replay -t <task_id>`，您可以为重放过程指定 `task_id`。 

Kickoff 现在将在本地保存最新 kickoff 返回的任务输出，以便您能够从中重放。


### 使用 CLI 从特定任务重放
要使用重放功能，请按照以下步骤操作：

1. 打开终端或命令提示符。
2. 导航到您的 CrewAI 项目所在的目录。
3. 运行以下命令：

要查看最新的 kickoff task_id，请使用：

```shell
crewai log-tasks-outputs
```


```shell
crewai replay -t <task_id>
```

这些命令允许您从最新的 kickoff 任务重放，同时保留先前执行任务的上下文。
