---
title: crewAI 工具
description: 了解和利用 crewAI 框架中的工具进行 agent 协作和任务执行。
---

## 简介
crewAI 工具赋予 agent 各种能力，从网络搜索和数据分析到协作以及在同事之间委派任务。本文档概述了如何在 crewAI 框架内创建、集成和利用这些工具，包括对协作工具的新关注。

## 什么是工具？
!!! note "定义"
    crewAI 中的工具是 agent 可以利用的技能或功能，用于执行各种操作。这包括来自 [crewAI 工具包](https://github.com/aithoughts/aipmAI-tools) 和 [LangChain 工具](https://python.langchain.com/docs/integrations/tools) 的工具，支持从简单搜索到复杂交互以及 agent 之间的有效团队合作。

## 工具的主要特点

- **实用性**: 为网络搜索、数据分析、内容生成和 agent 协作等任务而设计。
- **集成**: 通过将工具无缝集成到 agent 的工作流程中来增强其能力。
- **可定制性**: 提供开发自定义工具或利用现有工具的灵活性，以满足 agent 的特定需求。
- **错误处理**:  结合了强大的错误处理机制，以确保平稳运行。
- **缓存机制**:  具有智能缓存功能，可优化性能并减少冗余操作。

## 使用 crewAI 工具

要使用 crewAI 工具增强您的 agent 的能力，请先安装我们的额外工具包：

```bash
pip install 'crewai[tools]'
```

以下是一个演示如何使用它们的示例：

```python
import os
from crewai import Agent, Task, Crew
# 导入 crewAI 工具
from crewai_tools import (
    DirectoryReadTool,
    FileReadTool,
    SerperDevTool,
    WebsiteSearchTool
)

# 设置 API 密钥
os.environ["SERPER_API_KEY"] = "您的密钥" # serper.dev API 密钥
os.environ["OPENAI_API_KEY"] = "您的密钥"

# 实例化工具
docs_tool = DirectoryReadTool(directory='./blog-posts')
file_tool = FileReadTool()
search_tool = SerperDevTool()
web_rag_tool = WebsiteSearchTool()

# 创建 agent
researcher = Agent(
    role='市场研究分析师',
    goal='提供最新的 AI 行业市场分析',
    backstory='一位对市场趋势有敏锐洞察力的专家分析师。',
    tools=[search_tool, web_rag_tool],
    verbose=True
)

writer = Agent(
    role='内容撰稿人',
    goal='撰写有关 AI 行业的引人入胜的博客文章',
    backstory='一位热爱技术的熟练作家。',
    tools=[docs_tool, file_tool],
    verbose=True
)

# 定义任务
research = Task(
    description='研究 AI 行业的最新趋势并提供摘要。',
    expected_output='对 AI 行业排名前 3 位的趋势发展进行总结，并对其意义提出独特的见解。',
    agent=researcher
)

write = Task(
    description='根据研究分析师的摘要，撰写一篇关于 AI 行业的引人入胜的博客文章。从目录中最新博客文章中汲取灵感。',
    expected_output='一篇 4 段式的博客文章，采用 markdown 格式，内容引人入胜、信息丰富且通俗易懂，避免使用复杂的术语。',
    agent=writer,
    output_file='blog-posts/new_post.md'  # 最终的博客文章将保存在此处
)

# 组建 crew
crew = Crew(
    agents=[researcher, writer],
    tasks=[research, write],
    verbose=2
)

# 执行任务
crew.kickoff()
```

## 可用的 crewAI 工具

- **错误处理**: 所有工具都内置了错误处理功能，允许 agent 优雅地管理异常并继续执行任务。
- **缓存机制**: 所有工具都支持缓存，使 agent 能够有效地重用以前获得的结果，从而减少外部资源的负载并加快执行时间。您还可以使用工具上的 `cache_function` 属性对缓存机制进行更精细的控制。

以下是可用工具及其描述的列表：

| 工具                        | 描述                                                                                   |
| :-------------------------- | :-------------------------------------------------------------------------------------------- |
| **BrowserbaseLoadTool**     | 用于与网络浏览器交互和从中提取数据的工具。                            |
| **CodeDocsSearchTool**      | 针对搜索代码文档和相关技术文档进行了优化的 RAG 工具。 |
| **CodeInterpreterTool**     | 用于解释 Python 代码的工具。                                                          |
| **ComposioTool**            | 支持使用 Composio 工具。                                                                |
| **CSVSearchTool**           | 专为在 CSV 文件中搜索而设计的 RAG 工具，专为处理结构化数据而定制。       |
| **DirectorySearchTool**     | 用于在目录中搜索的 RAG 工具，可用于浏览文件系统。      |
| **DOCXSearchTool**          | 旨在在 DOCX 文档中搜索的 RAG 工具，非常适合处理 Word 文件。         |
| **DirectoryReadTool**       | 促进对目录结构及其内容的读取和处理。                |
| **EXASearchTool**           | 专为跨各种数据源执行详尽搜索而设计的工具。               |
| **FileReadTool**            | 支持读取各种文件格式并从中提取数据。              |
| **FirecrawlSearchTool**     | 使用 Firecrawl 搜索网页并返回结果的工具。                             |
| **FirecrawlCrawlWebsiteTool** | 使用 Firecrawl 抓取网页的工具。                                               |
| **FirecrawlScrapeWebsiteTool** | 使用 Firecrawl 抓取网页 url 并返回其内容的工具。               |
| **GithubSearchTool**        | 用于在 GitHub 存储库中搜索的 RAG 工具，可用于代码和文档搜索。|
| **SerperDevTool**           | 用于开发目的的专用工具，具有正在开发的特定功能。 |
| **TXTSearchTool**           | 专注于在文本 (.txt) 文件中搜索的 RAG 工具，适用于非结构化数据。     |
| **JSONSearchTool**          | 专为在 JSON 文件中搜索而设计的 RAG 工具，适用于结构化数据处理。     |
| **LlamaIndexTool**          | 支持使用 LlamaIndex 工具。                                                          |
| **MDXSearchTool**           | 专为在 Markdown (MDX) 文件中搜索而定制的 RAG 工具，适用于文档。      |
| **PDFSearchTool**           | 旨在在 PDF 文档中搜索的 RAG 工具，非常适合处理扫描文档。    |
| **PGSearchTool**            | 针对在 PostgreSQL 数据库中搜索进行了优化的 RAG 工具，适用于数据库查询。 |
| **RagTool**                 | 能够处理各种数据源和类型的通用 RAG 工具。                 |
| **ScrapeElementFromWebsiteTool** | 支持从网站抓取特定元素，适用于定向数据提取。     |
| **ScrapeWebsiteTool**       | 促进抓取整个网站，非常适合全面收集数据。                 |
| **WebsiteSearchTool**       | 用于搜索网站内容的 RAG 工具，针对网络数据提取进行了优化。                   |
| **XMLSearchTool**           | 专为在 XML 文件中搜索而设计的 RAG 工具，适用于结构化数据格式。      |
| **YoutubeChannelSearchTool**| 用于在 YouTube 频道中搜索的 RAG 工具，适用于视频内容分析。           |
| **YoutubeVideoSearchTool**  | 旨在在 YouTube 视频中搜索的 RAG 工具，非常适合视频数据提取。          |

## 创建您自己的工具

!!! example "自定义工具创建"
    开发人员可以根据其 agent 的需求定制工具，也可以利用预先构建的选项：

要创建您自己的 crewAI 工具，您需要安装我们的额外工具包：

```bash
pip install 'crewai[tools]'
```

完成此操作后，您可以通过两种主要方式创建 crewAI 工具：
### 子类化 `BaseTool`

```python
from crewai_tools import BaseTool

class MyCustomTool(BaseTool):
    name: str = "我的工具的名称"
    description: str = "清楚地描述此工具的用途，您的 agent 将需要此信息才能使用它。"

    def _run(self, argument: str) -> str:
        # 实现代码在此处
        return "自定义工具的结果"
```

### 利用 `tool` 装饰器

```python
from crewai_tools import tool
@tool("我的工具的名称")
def my_tool(question: str) -> str:
    """清楚地描述此工具的用途，您的 agent 将需要此信息才能使用它。"""
    # 函数逻辑在此处
    return "您的自定义工具的结果"
```

### 自定义缓存机制
!!! note "缓存"
    工具可以选择实现 `cache_function` 以微调缓存行为。此函数根据特定条件确定何时缓存结果，从而提供对缓存逻辑的精细控制。

```python
from crewai_tools import tool

@tool
def multiplication_tool(first_number: int, second_number: int) -> str:
    """当您需要将两个数字相乘时很有用。"""
    return first_number * second_number

def cache_func(args, result):
    # 在这种情况下，我们仅在结果是 2 的倍数时才缓存结果
    cache = result % 2 == 0
    return cache

multiplication_tool.cache_function = cache_func

writer1 = Agent(
        role="作家",
        goal="您为孩子们编写数学课本。",
        backstory="您是写作专家，并且喜欢教孩子们，但您对数学一无所知。",
        tools=[multiplication_tool],
        allow_delegation=False,
    )
    #...
```


## 结论
工具对于扩展 crewAI agent 的能力至关重要，使它们能够承担广泛的任务并有效地协作。使用 crewAI 构建解决方案时，请利用自定义工具和现有工具来增强您的 agent 的能力并增强 AI 生态系统。考虑利用错误处理、缓存机制和工具参数的灵活性来优化 agent 的性能和能力。

