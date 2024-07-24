# YoutubeVideoSearchTool 文档

!!! note "实验性"
    我们仍在努力改进工具，因此未来可能会更改本文档。
    :octicons-mark-github-16: [YoutubeVideoSearchTool 源代码](https://github.com/aithoughts/aipmAI-tools/tree/zh/src/crewai_tools/tools/youtube_video_search_tool)

## 描述

此工具是 `crewai_tools` 包的一部分，旨在利用检索增强生成 (RAG) 技术在 Youtube 视频内容中执行语义搜索。它是包中几个利用 RAG 处理不同来源的“搜索”工具之一。YoutubeVideoSearchTool 允许灵活搜索；用户无需指定视频 URL 即可搜索所有 Youtube 视频内容，也可以通过提供视频 URL 将搜索范围缩小到特定的 Youtube 视频。

## 安装

要使用 YoutubeVideoSearchTool，您必须先安装 `crewai_tools` 包。此包包含 YoutubeVideoSearchTool 以及其他旨在增强数据分析和处理任务的实用程序。通过在终端中执行以下命令来安装包：

```
pip install 'crewai[tools]'
```

## 示例

要将 YoutubeVideoSearchTool 集成到您的 Python 项目中，请遵循以下示例。这演示了如何将该工具用于一般 Youtube 内容搜索以及在特定视频内容中进行 targeted searches。

```python
from crewai_tools import YoutubeVideoSearchTool

# 对 Youtube 内容进行一般搜索而不指定视频 URL，以便代理可以在其操作期间了解其 URL 的任何 Youtube 视频内容中进行搜索
tool = YoutubeVideoSearchTool()

# 在特定 Youtube 视频内容中进行 targeted searches
tool = YoutubeVideoSearchTool(youtube_video_url='https://youtube.com/watch?v=example')
```

## 参数

YoutubeVideoSearchTool 接受以下初始化参数：

- `youtube_video_url`：初始化时的可选参数，但如果针对特定 Youtube 视频，则为必需参数。它指定了您要在其中进行搜索的 Youtube 视频 URL 路径。

## 自定义模型和嵌入

默认情况下，该工具使用 OpenAI 进行嵌入和摘要。要自定义模型，可以使用如下配置字典：

```python
tool = YoutubeVideoSearchTool(
    config=dict(
        llm=dict(
            provider="ollama", # 或 google、openai、anthropic、llama2 等
            config=dict(
                model="llama2",
                # temperature=0.5,
                # top_p=1,
                # stream=true,
            ),
        ),
        embedder=dict(
            provider="google", # 或 openai、ollama 等
            config=dict(
                model="models/embedding-001",
                task_type="retrieval_document",
                # title="Embeddings",
            ),
        ),
    )
)
```
