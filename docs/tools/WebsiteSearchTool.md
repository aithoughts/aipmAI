# WebsiteSearchTool 文档

!!! note "实验性"
    我们仍在努力改进工具，因此未来可能会更改本文档。
    :octicons-mark-github-16: [WebsiteSearchTool 源代码](https://github.com/aithoughts/aipmAI-tools/tree/zh/src/crewai_tools/tools/website_search_tool)

## 描述
WebsiteSearchTool 旨在作为一种在网站内容中进行语义搜索的概念工具。它旨在利用检索增强生成 (RAG) 等先进的机器学习模型，以高效地导航和提取指定 URL 中的信息。此工具旨在提供灵活性，允许用户在任何网站上执行搜索或专注于感兴趣的特定网站。请注意，WebsiteSearchTool 的当前实现细节仍在开发中，其所述功能可能尚不可用。

## 安装
为了在 WebsiteSearchTool 可用时准备好您的环境，您可以使用以下命令安装基础包：

```shell
pip install 'crewai[tools]'
```

此命令将安装必要的依赖项，以确保在工具完全集成后，用户可以立即开始使用它。

## 示例用法
以下是 WebsiteSearchTool 在不同场景中如何使用的示例。请注意，这些示例仅供说明，代表计划的功能：

```python
from crewai_tools import WebsiteSearchTool

# 启动代理可以用来搜索任何发现的网站的工具示例
tool = WebsiteSearchTool()

# 将搜索范围限制在特定网站内容的示例，因此现在代理只能在该网站内进行搜索
tool = WebsiteSearchTool(website='https://example.com')
```

## 参数
- `website`：一个可选参数，用于指定用于 focused searches 的网站 URL。此参数旨在通过在必要时允许 targeted searches 来增强工具的灵活性。

## 自定义选项
默认情况下，该工具使用 OpenAI 进行嵌入和摘要。要自定义模型，可以使用如下配置字典：


```python
tool = WebsiteSearchTool(
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
