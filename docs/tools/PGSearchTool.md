# PGSearchTool 文档

!!! note "实验性"
    我们仍在努力改进工具，因此未来可能会更改本文档。
    :octicons-mark-github-16: [PGSearchTool 源代码](https://github.com/aithoughts/aipmAI-tools/tree/zh/src/crewai_tools/tools/pg_search_tool)

## 描述
PGSearchTool 被设想为一种强大的工具，用于促进 PostgreSQL 数据库表中的语义搜索。通过利用先进的检索和生成 (RAG) 技术，它旨在提供一种高效的查询数据库表内容的方式，专门针对 PostgreSQL 数据库量身定制。该工具的目标是通过语义搜索查询简化查找相关数据的过程，为需要在 PostgreSQL 环境中的大型数据集上执行高级查询的用户提供宝贵的资源。

## 安装
包含 PGSearchTool（发布后）的 `crewai_tools` 包可以使用以下命令安装：

```shell
pip install 'crewai[tools]'
```

（注意：PGSearchTool 在当前版本的 `crewai_tools` 包中尚不可用。该工具发布后，此安装命令将更新。）

## 示例用法
以下是一个建议示例，展示了如何使用 PGSearchTool 对 PostgreSQL 数据库中的表执行语义搜索：

```python
from crewai_tools import PGSearchTool

# 使用数据库 URI 和目标表名初始化工具
tool = PGSearchTool(db_uri='postgresql://user:password@localhost:5432/mydatabase', table_name='employees')
```

## 参数
PGSearchTool 需要以下参数才能运行：

- `db_uri`：表示要查询的 PostgreSQL 数据库的 URI 的字符串。此参数将是必需的，并且必须包含必要的身份验证详细信息和数据库的位置。
- `table_name`：指定将在其上执行语义搜索的数据库中表的名称的字符串。此参数也是必需的。

## 自定义模型和嵌入

默认情况下，该工具打算使用 OpenAI 进行嵌入和摘要。用户可以选择使用如下配置字典自定义模型：

```python
tool = PGSearchTool(
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
