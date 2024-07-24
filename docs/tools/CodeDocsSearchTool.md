# CodeDocsSearchTool 文档

!!! note "实验性"
    我们仍在努力改进工具，因此未来可能会更改本文档。
    :octicons-mark-github-16: [CodeDocsSearchTool 源代码](https://github.com/aithoughts/aipmAI-tools/tree/zh/src/crewai_tools/tools/code_docs_search_tool)

## 描述

CodeDocsSearchTool 是一款强大的 RAG（检索增强生成）工具，旨在在代码文档中进行语义搜索。它使用户能够在代码文档中高效地找到特定信息或主题。通过在初始化期间提供 `docs_url`，该工具可以将搜索范围缩小到特定的文档站点。或者，如果没有特定的 `docs_url`，它会在其执行过程中搜索已知或发现的各种代码文档，使其适用于各种文档搜索需求。

## 安装

要开始使用 CodeDocsSearchTool，首先，通过 pip 安装 crewai_tools 包：

```
pip install 'crewai[tools]'
```

## 示例

如下所示使用 CodeDocsSearchTool 在代码文档中进行搜索：

```python
from crewai_tools import CodeDocsSearchTool

# 如果在执行期间知道或发现了 URL，则搜索任何代码文档内容：
tool = CodeDocsSearchTool()

# 或

# 通过提供文档 URL 来专门将搜索重点放在给定的文档站点上：
tool = CodeDocsSearchTool(docs_url='https://docs.example.com/reference')
```
注意：将 'https://docs.example.com/reference' 替换为您的目标文档 URL，并将 'How to use search tool' 替换为与您的需求相关的搜索查询。

## 参数

- `docs_url`：可选。指定要搜索的代码文档的 URL。在工具初始化期间提供此参数会将搜索重点放在指定的文档内容上。

## 自定义模型和嵌入

默认情况下，该工具使用 OpenAI 进行嵌入和摘要。要自定义模型，可以使用如下配置字典：

```python
tool = CodeDocsSearchTool(
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
