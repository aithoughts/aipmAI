# YoutubeChannelSearchTool 文档

!!! note "实验性"
    我们仍在努力改进工具，因此未来可能会更改本文档。
    :octicons-mark-github-16: [YoutubeChannelSearchTool 源代码](https://github.com/aithoughts/aipmAI-tools/tree/zh/src/crewai_tools/tools/youtube_channel_search_tool)

## 描述
此工具旨在在特定 Youtube 频道的内容中执行语义搜索。它利用 RAG（检索增强生成）方法，提供相关的搜索结果，使其成为提取信息或查找特定内容的宝贵工具，而无需手动筛选视频。它简化了 Youtube 频道内的搜索过程，满足了研究人员、内容创作者和寻求特定信息或主题的观众的需求。

## 安装
要使用 YoutubeChannelSearchTool，必须安装 `crewai_tools` 包。在您的 shell 中执行以下命令进行安装：

```shell
pip install 'crewai[tools]'
```

## 示例
要开始使用 YoutubeChannelSearchTool，请遵循以下示例。这演示了如何使用特定的 Youtube 频道句柄初始化工具，并在该频道的内容中进行搜索。

```python
from crewai_tools import YoutubeChannelSearchTool

# 初始化工具以在代理执行期间了解的任何 Youtube 频道内容中进行搜索
tool = YoutubeChannelSearchTool()

# 或

# 使用特定的 Youtube 频道句柄初始化工具以定位您的搜索
tool = YoutubeChannelSearchTool(youtube_channel_handle='@exampleChannel')
```

## 参数
- `youtube_channel_handle` ：表示 Youtube 频道句柄的必填字符串。此参数对于初始化工具以指定要在其中进行搜索的频道至关重要。该工具旨在仅在提供的频道句柄的内容中进行搜索。

## 自定义模型和嵌入

默认情况下，该工具使用 OpenAI 进行嵌入和摘要。要自定义模型，可以使用如下配置字典：

```python
tool = YoutubeChannelSearchTool(
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
