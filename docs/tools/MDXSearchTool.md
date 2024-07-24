# MDXSearchTool 文档

!!! note "实验性"
    我们仍在努力改进工具，因此未来可能会更改本文档。
    :octicons-mark-github-16: [MDXSearchTool 源代码](https://github.com/aithoughts/aipmAI-tools/tree/zh/src/crewai_tools/tools/mdx_search_tool)

## 描述
MDX 搜索工具是 `crewai_tools` 包中的一个组件，旨在促进高级 Markdown 语言提取。它使用户能够使用基于查询的搜索有效地从 MD 文件中搜索和提取相关信息。此工具对于数据分析、信息管理和研究任务非常宝贵，简化了在大型文档集合中查找特定信息的过程。

## 安装
在使用 MDX 搜索工具之前，请确保已安装 `crewai_tools` 包。如果未安装，可以使用以下命令安装：

```shell
pip install 'crewai[tools]'
```

## 使用示例
要使用 MDX 搜索工具，您必须首先设置必要的环境变量。然后，将该工具集成到您的 crewAI 项目中，以开始您的市场调查。以下是有关如何执行此操作的基本示例：

```python
from crewai_tools import MDXSearchTool

# 初始化工具以搜索执行期间了解的任何 MDX 内容
tool = MDXSearchTool()

# 或

# 使用特定的 MDX 文件路径初始化工具，以便在该文档中进行独占搜索
tool = MDXSearchTool(mdx='path/to/your/document.mdx')
```

## 参数
- mdx：**可选**。指定要搜索的 MDX 文件的路径。可以在初始化期间提供。

## 模型和嵌入的自定义

该工具默认使用 OpenAI 进行嵌入和摘要。要进行自定义，请使用如下所示的配置字典：

```python
tool = MDXSearchTool(
    config=dict(
        llm=dict(
            provider="ollama", # 选项包括 google、openai、anthropic、llama2 等。
            config=dict(
                model="llama2",
                # 可选参数可以包含在此处。
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
                # 可在此处添加嵌入的可选标题。
                # title="Embeddings",
            ),
        ),
    )
)
```
