# TXTSearchTool 文档

!!! note "实验性"
    我们仍在努力改进工具，因此未来可能会更改本文档。
    :octicons-mark-github-16: [TXTSearchTool 源代码](https://github.com/aithoughts/aipmAI-tools/tree/zh/src/crewai_tools/tools/txt_search_tool)

## 描述
此工具用于在文本文件的内容中执行 RAG（检索增强生成）搜索。它允许在指定的文本文件内容中对查询进行语义搜索，使其成为根据提供的查询快速提取信息或查找特定文本段落的宝贵资源。

## 安装
要使用 TXTSearchTool，您首先需要安装 crewai_tools 包。这可以使用 pip（Python 的包管理器）来完成。打开您的终端或命令提示符并输入以下命令：

```shell
pip install 'crewai[tools]'
```

此命令将下载并安装 TXTSearchTool 以及任何必要的依赖项。

## 示例
以下示例演示了如何使用 TXTSearchTool 在文本文件中进行搜索。此示例显示了使用特定文本文件初始化工具以及随后在该文件内容中进行搜索。

```python
from crewai_tools import TXTSearchTool

# 初始化工具以在代理执行期间了解的任何文本文件内容中进行搜索
tool = TXTSearchTool()

# 或

# 使用特定的文本文件初始化工具，以便代理可以在给定的文本文件内容中进行搜索
tool = TXTSearchTool(txt='path/to/text/file.txt')
```

## 参数
- `txt` (str): **可选**。要搜索的文本文件的路径。仅当未初始化带有特定文本文件的工具时才需要此参数；否则，将在最初提供的文本文件中执行搜索。

## 自定义模型和嵌入

默认情况下，该工具使用 OpenAI 进行嵌入和摘要。要自定义模型，可以使用如下配置字典：

```python
tool = TXTSearchTool(
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
