# GithubSearchTool 文档

!!! note "实验性"
    我们仍在努力改进工具，因此未来可能会更改本文档。
    :octicons-mark-github-16: [GithubSearchTool 源代码](https://github.com/aithoughts/aipmAI-tools/tree/zh/src/crewai_tools/tools/github_search_tool)

## 描述
GithubSearchTool 是一款专门设计用于在 GitHub 存储库中执行语义搜索的检索增强生成 (RAG) 工具。它利用先进的语义搜索功能，筛选代码、拉取请求、问题和存储库，使其成为开发人员、研究人员或任何需要从 GitHub 获取精确信息的人员必不可少的工具。

## 安装
要使用 GithubSearchTool，首先请确保在您的 Python 环境中安装了 crewai_tools 包：

```shell
pip install 'crewai[tools]'
```

此命令将安装运行 GithubSearchTool 所需的包以及 crewai_tools 包中包含的任何其他工具。

## 示例
以下是如何使用 GithubSearchTool 在 GitHub 存储库中执行语义搜索：
```python
from crewai_tools import GithubSearchTool

# 初始化工具以在特定的 GitHub 存储库中进行语义搜索
tool = GithubSearchTool(
	github_repo='https://github.com/example/repo',
	content_types=['code', 'issue'] # 选项：code、repo、pr、issue
)

# 或

# 初始化工具以在特定的 GitHub 存储库中进行语义搜索，以便代理可以在执行期间了解任何存储库并进行搜索
tool = GithubSearchTool(
	content_types=['code', 'issue'] # 选项：code、repo、pr、issue
)
```

## 参数
- `github_repo` ：将在其中进行搜索的 GitHub 存储库的 URL。这是一个必填字段，用于指定搜索的目标存储库。
- `content_types` ：指定要在搜索中包含的内容类型。您必须从以下选项中提供一个内容类型列表：`code` 用于在代码中搜索，`repo` 用于在存储库的一般信息中搜索，`pr` 用于在拉取请求中搜索，以及 `issue` 用于在问题中搜索。此字段是必填字段，允许将搜索范围缩小到 GitHub 存储库中的特定内容类型。

## 自定义模型和嵌入

默认情况下，该工具使用 OpenAI 进行嵌入和摘要。要自定义模型，可以使用如下配置字典：

```python
tool = GithubSearchTool(
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
