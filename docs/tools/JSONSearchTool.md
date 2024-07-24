# JSONSearchTool 文档

!!! note "实验性"
    我们仍在努力改进工具，因此未来可能会更改本文档。
    :octicons-mark-github-16: [JSONSearchTool 源代码](https://github.com/aithoughts/aipmAI-tools/tree/zh/src/crewai_tools/tools/json_search_tool)

## 描述
JSONSearchTool 旨在促进对 JSON 文件内容进行高效、精确的搜索。它利用 RAG（检索和生成）搜索机制，允许用户指定 JSON 路径以便在特定 JSON 文件中进行 targeted searches。此功能显著提高了搜索结果的准确性和相关性。

## 安装
要安装 JSONSearchTool，请使用以下 pip 命令：

```shell
pip install 'crewai[tools]'
```

## 使用示例
以下是如何有效利用 JSONSearchTool 在 JSON 文件中进行搜索的更新示例。这些示例考虑了代码库中标识的当前实现和使用模式。

```python
from crewai.json_tools import JSONSearchTool  # 更新的导入路径

# 常规 JSON 内容搜索
# 当 JSON 路径事先已知或可以动态识别时，此方法适用。
tool = JSONSearchTool()

# 将搜索限制在特定的 JSON 文件
# 当您希望将搜索范围限制在特定的 JSON 文件时，请使用此初始化方法。
tool = JSONSearchTool(json_path='./path/to/your/file.json')
```

## 参数
- `json_path`（字符串，可选）：指定要搜索的 JSON 文件的路径。如果工具初始化为进行常规搜索，则不需要此参数。如果提供，它会将搜索范围限制在指定的 JSON 文件中。

## 配置选项
JSONSearchTool 支持通过配置字典进行广泛的自定义。这允许用户根据他们的需求选择不同的嵌入和摘要模型。

```python
tool = JSONSearchTool(
    config={
        "llm": {
            "provider": "ollama",  # 其他选项包括 google、openai、anthropic、llama2 等。
            "config": {
                "model": "llama2",
                # 其他可选配置可以在这里指定。
                # temperature=0.5,
                # top_p=1,
                # stream=true,
            },
        },
        "embedder": {
            "provider": "google", # 或 openai、ollama 等
            "config": {
                "model": "models/embedding-001",
                "task_type": "retrieval_document",
                # 可以在此处添加其他自定义选项。
            },
        },
    }
)
```
