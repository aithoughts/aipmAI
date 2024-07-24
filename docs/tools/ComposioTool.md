# ComposioTool 文档

!!! note "实验性"
    我们仍在努力改进工具，因此未来可能会更改本文档。
    :octicons-mark-github-16: [ComposioTool 源代码](https://github.com/aithoughts/aipmAI-tools/tree/zh/src/crewai_tools/tools/composio_tool)

## 描述

此工具是 [composio](https://composio.dev) 工具集的封装，使您的代理可以访问 composio SDK 中的各种工具。

## 安装

要将此工具集成到您的项目中，请按照以下安装说明进行操作：

```shell
pip install composio-core
pip install 'crewai[tools]'
```

安装完成后，运行 `composio login` 或将您的 composio API 密钥导出为 `COMPOSIO_API_KEY`。

## 示例

以下示例演示了如何初始化工具并执行 github 操作：

1. 初始化工具集

```python
from composio import App
from crewai_tools import ComposioTool
from crewai import Agent, Task


tools = [ComposioTool.from_action(action=Action.GITHUB_ACTIVITY_STAR_REPO_FOR_AUTHENTICATED_USER)]
```

如果您不知道要使用什么操作，请使用 `from_app` 和 `tags` 过滤器获取相关操作

```python
tools = ComposioTool.from_app(App.GITHUB, tags=["important"])
```

或使用 `use_case` 搜索相关操作

```python
tools = ComposioTool.from_app(App.GITHUB, use_case="Star a github repository")
```

2. 定义代理

```python
crewai_agent = Agent(
    role="Github 代理",
    goal="您使用 Github API 对 Github 执行操作",
    backstory=(
        "您是一个 AI 代理，负责代表用户对 Github 执行操作。"
        "您需要使用 Github API 对 Github 执行操作"
    ),
    verbose=True,
    tools=tools,
)
```

3. 执行任务

```python
task = Task(
    description="在 GitHub 上为 ComposioHQ/composio 仓库点赞",
    agent=crewai_agent,
    expected_output="如果点赞成功",
)

task.execute()
```

* 更详细的工具列表可以在 [此处](https://app.composio.dev) 找到
