## CrewAI

<div align="center">

![CrewAI 的 Logo，两个人在一艘船上划船](./docs/crewai_logo.png)

🤖 **crewAI**: 用于编排角色扮演、自主 AI 代理的尖端框架。通过促进协作智能，CrewAI 使代理能够无缝地协同工作，处理复杂的任务。

<h3>

[主页](https://www.theforage.cn/) | [aipmAI - crewAI 中文解决方案](https://aipm-docs.theforage.cn/) | [与文档聊天](https://chatg.pt/DWjSBZn) | [示例](https://github.com/aithoughts/aipmAI-examples) | [Discord](https://discord.com/invite/X4JWnZnxPb)

</h3>

[![GitHub Repo stars](https://img.shields.io/github/stars/aithoughts/aipmAI)](https://github.com/aithoughts/aipmAI)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

</div>

## 目录

- [为什么选择 CrewAI？](#为什么选择-crewai)
- [入门](#入门)
- [主要功能](#主要功能)
- [示例](#示例)
  - [快速教程](#快速教程)
  - [编写职位描述](#编写职位描述)
  - [旅行计划](#旅行计划)
  - [股票分析](#股票分析)
- [将您的团队连接到模型](#将您的团队连接到模型)
- [CrewAI 的比较](#crewai-的比较)
- [贡献](#贡献)
- [遥测](#遥测)
- [许可证](#许可证)

## 为什么选择 CrewAI？

AI 协作的力量不容忽视。
CrewAI 旨在使 AI 代理能够承担角色、共享目标并以一个有凝聚力的单元运作——就像一支配合默契的团队一样。无论您是在构建智能助手平台、自动化客户服务团队还是多代理研究团队，CrewAI 都能为复杂的多代理交互提供支柱。

## 入门

要开始使用 CrewAI，请按照以下简单步骤操作：

### 1. 安装

```shell
pip install crewai
```

如果您想安装“crewai”包及其可选功能（包括用于代理的其他工具），可以使用以下命令：pip install 'crewai[tools]'。此命令将安装基本软件包，并添加需要更多依赖项才能运行的额外组件。

```shell
pip install 'crewai[tools]'
```

### 2. 设置您的团队

```python
import os
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"
os.environ["SERPER_API_KEY"] = "Your Key" # serper.dev API 密钥

# 您可以选择通过 Ollama 使用本地模型。有关更多信息，请参阅 https://docs.crewai.com/how-to/LLM-Connections/。

# os.environ["OPENAI_API_BASE"] = 'http://localhost:11434/v1'
# os.environ["OPENAI_MODEL_NAME"] ='openhermes'  # 根据可用模型进行调整
# os.environ["OPENAI_API_KEY"] ='sk-111111111111111111111111111111111111111111111111'

# 您可以传递一个可选的 llm 属性，指定您想使用的模型。
# 它可以是通过 Ollama / LM Studio 的本地模型，也可以是远程模型
# 模型，如 OpenAI、Mistral、Antrophic 或其他（https://docs.crewai.com/how-to/LLM-Connections/）
#
# import os
# os.environ['OPENAI_MODEL_NAME'] = 'gpt-3.5-turbo'
#
# 或
#
# from langchain_openai import ChatOpenAI

search_tool = SerperDevTool()

# 定义您的代理，包括角色和目标
researcher = Agent(
  role='高级研究分析师',
  goal='发现人工智能和数据科学领域的尖端发展',
  backstory="""您在一家领先的科技智库工作。
  您的专长是识别新兴趋势。
  您有剖析复杂数据并提出可操作见解的诀窍。""",
  verbose=True,
  allow_delegation=False,
  # 您可以传递一个可选的 llm 属性，指定您想使用的模型。
  # llm=ChatOpenAI(model_name="gpt-3.5", temperature=0.7),
  tools=[search_tool]
)
writer = Agent(
  role='科技内容策略师',
  goal='撰写关于科技进步的引人入胜的内容',
  backstory="""您是一位著名的内容策略师，以您富有洞察力和吸引力的文章而闻名。
  您将复杂的 koncepty 转化为引人入胜的叙述。""",
  verbose=True,
  allow_delegation=True
)

# 为您的代理创建任务
task1 = Task(
  description="""对 2024 年人工智能的最新进展进行全面分析。
  确定关键趋势、突破性技术和潜在的行业影响。""",
  expected_output="以要点形式完整分析报告",
  agent=researcher
)

task2 = Task(
  description="""利用所提供的见解，撰写一篇引人入胜的博客文章，
  重点介绍最重要的人工智能进步。
  您的文章应该信息丰富且通俗易懂，面向精通技术的受众。
  让它听起来很酷，避免使用复杂的词语，这样听起来就不会像人工智能。""",
  expected_output="至少包含 4 段的完整博客文章",
  agent=writer
)

# 使用顺序流程实例化您的团队
crew = Crew(
  agents=[researcher, writer],
  tasks=[task1, task2],
  verbose=2, # 您可以将其设置为 1 或 2 以获得不同的日志记录级别
  process = Process.sequential
)

# 让您的团队开始工作！
result = crew.kickoff()

print("######################")
print(result)
```

除了顺序流程之外，您还可以使用分层流程，该流程会自动为定义的团队分配一名经理，以通过委派和验证结果来正确协调任务的计划和执行。[在此处了解更多关于流程的信息](https://docs.crewai.com/core-concepts/Processes/)。

## 主要功能

- **基于角色的代理设计**: 使用特定的角色、目标和工具自定义代理。
- **自主的代理间委派**: 代理可以自主地委派任务并在彼此之间进行询问，从而提高解决问题的效率。
- **灵活的任务管理**: 使用可自定义的工具定义任务，并动态地将它们分配给代理。
- **流程驱动**: 目前仅支持“顺序”任务执行和“分层”流程，但正在开发更复杂的流程，如协商一致和自主流程。
- **将输出保存为文件**: 将单个任务的输出保存为文件，以便您以后使用。
- **将输出解析为 Pydantic 或 Json**: 如果您希望将单个任务的输出解析为 Pydantic 模型或 Json，可以这样做。
- **与开源模型配合使用**: 使用 Open AI 或开源模型运行您的团队，请参阅 [将 crewAI 连接到 LLM](https://docs.crewai.com/how-to/LLM-Connections/) 页面，了解有关配置您的代理与模型（甚至是本地运行的模型）连接的详细信息！

![CrewAI 思维导图](./docs/crewAI-mindmap.png "CrewAI 思维导图")

## 示例

您可以在 [crewAI-examples 仓库](https://github.com/aithoughts/aipmai-examples?tab=readme-ov-file) 中测试 AI 团队在现实生活中的不同示例：

- [登录页面生成器](https://github.com/aithoughts/aipmai-examples/tree/main/landing_page_generator)
- [在执行过程中获得人工输入](https://docs.crewai.com/how-to/Human-Input-on-Execution)
- [旅行计划](https://github.com/aithoughts/aipmai-examples/tree/main/trip_planner)
- [股票分析](https://github.com/aithoughts/aipmai-examples/tree/main/stock_analysis)

### 快速教程

[![CrewAI 教程](https://img.youtube.com/vi/tnejrr-0a94/maxresdefault.jpg)](https://www.youtube.com/watch?v=tnejrr-0a94 "CrewAI 教程")

### 编写职位描述

[查看此示例的代码](https://github.com/aithoughts/aipmai-examples/tree/main/job-posting) 或观看以下视频：

[![职位发布](https://img.youtube.com/vi/u98wEMz-9to/maxresdefault.jpg)](https://www.youtube.com/watch?v=u98wEMz-9to "职位发布")

### 旅行计划

[查看此示例的代码](https://github.com/aithoughts/aipmai-examples/tree/main/trip_planner) 或观看以下视频：

[![旅行计划](https://img.youtube.com/vi/xis7rWp-hjs/maxresdefault.jpg)](https://www.youtube.com/watch?v=xis7rWp-hjs "旅行计划")

### 股票分析

[查看此示例的代码](https://github.com/aithoughts/aipmai-examples/tree/main/stock_analysis) 或观看以下视频：

[![股票分析](https://img.youtube.com/vi/e0Uj4yWdaAg/maxresdefault.jpg)](https://www.youtube.com/watch?v=e0Uj4yWdaAg "股票分析")

## 将您的团队连接到模型

crewAI 支持通过各种连接选项使用各种 LLM。默认情况下，您的代理在查询模型时将使用 OpenAI API。但是，还有其他几种方法可以让您的代理连接到模型。例如，您可以将代理配置为通过 Ollama 工具使用本地模型。

有关配置代理与模型连接的详细信息，请参阅 [将 crewAI 连接到 LLM](https://docs.crewai.com/how-to/LLM-Connections/) 页面。

## CrewAI 的比较

- **Autogen**: 虽然 Autogen 在创建能够协同工作的对话代理方面做得很好，但它缺乏对流程的内生概念。在 Autogen 中，协调代理的交互需要额外的编程，随着任务规模的增长，这可能会变得复杂而繁琐。

- **ChatDev**: ChatDev 将流程的概念引入了 AI 代理领域，但其实现相当僵化。ChatDev 中的自定义选项有限，并且不适合生产环境，这可能会阻碍现实世界应用程序的可扩展性和灵活性。

**CrewAI 的优势**: CrewAI 在构建时就考虑到了生产环境。它提供了 Autogen 对话代理的灵活性和 ChatDev 的结构化流程方法，但没有僵化性。CrewAI 的流程设计灵活且可适应，可以无缝地融入开发和生产工作流程。


## 贡献

CrewAI 是开源的，我们欢迎大家做出贡献。如果您希望做出贡献，请：

- 分叉存储库。
- 为您的功能创建一个新的分支。
- 添加您的功能或改进。
- 发送拉取请求。
- 我们感谢您的投入！

### 安装依赖项

```bash
poetry lock
poetry install
```

### 虚拟环境

```bash
poetry shell
```

### 预提交钩子

```bash
pre-commit install
```

### 运行测试

```bash
poetry run pytest
```

### 运行静态类型检查

```bash
poetry run mypy
```

### 打包

```bash
poetry build
```

### 本地安装

```bash
pip install dist/*.tar.gz
```

## 遥测

CrewAI 使用匿名遥测来收集使用数据，其主要目的是通过将我们的工作重点放在最常用的功能、集成和工具上来帮助我们改进库。

我们不会收集有关提示、任务描述、代理背景故事或目标、工具使用、API 调用、响应或代理正在处理的任何数据、任何密钥和环境变量的数据。

收集的数据包括：

- CrewAI 的版本
  - 因此我们可以了解有多少用户在使用最新版本
- Python 的版本
  - 因此我们可以决定更好地支持哪些版本
- 常规操作系统（例如 CPU 数量、macOS/Windows/Linux）
  - 因此我们知道应该重点关注哪些操作系统，以及我们是否可以构建特定于操作系统的功能
- 团队中的代理和任务数量
  - 因此我们可以确保我们在内部使用类似的用例进行测试，并向人们传授最佳实践
- 正在使用的团队流程
  - 了解我们应该在哪里集中精力
- 代理是否正在使用内存或允许委派
  - 了解我们是否改进了这些功能，或者甚至可以删除它们
- 任务是并行执行还是顺序执行
  - 了解我们是否应该更多地关注并行执行
- 正在使用的语言模型
  - 改进对最常用语言的支持
- 团队中代理的角色
  - 了解高级用例，以便我们可以构建更好的工具、集成和相关示例
- 可用工具的名称
  - 了解在公开可用的工具中，哪些工具使用最多，以便我们改进它们

用户可以通过在其团队上将 `share_crew` 属性设置为 `True` 来选择共享完整的遥测数据。

## 许可证

CrewAI 根据 MIT 许可证发布。
