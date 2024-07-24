# PDFSearchTool 文档

!!! note "实验性"
    我们仍在努力改进工具，因此未来可能会更改本文档。
    :octicons-mark-github-16: [PDFSearchTool 源代码](https://github.com/aithoughts/aipmAI-tools/tree/zh/src/crewai_tools/tools/pdf_search_tool)

## 描述
PDFSearchTool 是一款专为在 PDF 内容中进行语义搜索而设计的 RAG 工具。它允许输入搜索查询和 PDF 文档，利用先进的搜索技术高效地查找相关内容。此功能使其特别适用于从大型 PDF 文件中快速提取特定信息。

## 安装
要开始使用 PDFSearchTool，首先请确保使用以下命令安装了 crewai_tools 包：

```shell
pip install 'crewai[tools]'
```

## 示例
以下是如何使用 PDFSearchTool 在 PDF 文档中进行搜索：

```python
from crewai_tools import PDFSearchTool

# 初始化工具，如果在执行期间提供了路径，则允许进行任何 PDF 内容搜索
tool = PDFSearchTool()

# 或

# 使用特定的 PDF 路径初始化工具，以便仅在该文档中进行搜索
tool = PDFSearchTool(pdf='path/to/your/document.pdf')
```

## 参数
- `pdf`：**可选** 用于搜索的 PDF 路径。可以在初始化时或在 `run` 方法的参数中提供。如果在初始化时提供，则该工具会将其搜索范围限制在指定的文档内。

## 自定义模型和嵌入

默认情况下，该工具使用 OpenAI 进行嵌入和摘要。要自定义模型，可以使用如下配置字典：

```python
tool = PDFSearchTool(
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
