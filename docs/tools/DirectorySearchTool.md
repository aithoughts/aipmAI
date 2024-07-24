# DirectorySearchTool 文档

!!! note "实验性"
    我们仍在努力改进工具，因此未来可能会更改本文档。
    :octicons-mark-github-16: [DirectorySearchTool 源代码](https://github.com/aithoughts/aipmAI-tools/tree/zh/src/crewai_tools/tools/directory_search_tool)

## 描述
DirectorySearchTool 支持在指定目录的内容中进行语义搜索，利用检索增强生成 (RAG) 方法有效地导航文件。它专为灵活性而设计，允许用户在运行时动态指定搜索目录或在初始设置期间设置固定目录。

## 安装
要使用 DirectorySearchTool，首先安装 crewai_tools 包。在您的终端中执行以下命令：

```shell
pip install 'crewai[tools]'
```

## 初始化和使用
从 `crewai_tools` 包导入 DirectorySearchTool 以开始使用。您可以初始化该工具而不指定目录，从而能够在运行时设置搜索目录。或者，可以使用预定义目录初始化该工具。

```python
from crewai_tools import DirectorySearchTool

# 用于在运行时动态指定目录
tool = DirectorySearchTool()

# 用于固定目录搜索
tool = DirectorySearchTool(directory='/path/to/directory')
```

## 参数
- `directory`：指定搜索目录的字符串参数。这在初始化期间是可选的，但如果最初未设置，则搜索时需要。

## 自定义模型和嵌入
默认情况下，DirectorySearchTool 使用 OpenAI 进行嵌入和摘要。这些设置的自定义选项包括更改模型提供者和配置，从而增强了高级用户的灵活性。

```python
tool = DirectorySearchTool(
    config=dict(
        llm=dict(
            provider="ollama", # 选项包括 ollama、google、anthropic、llama2 等
            config=dict(
                model="llama2",
                # 其他配置在此处
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
