# CodeInterpreterTool 文档

!!! note "实验性"
    我们仍在努力改进工具，因此未来可能会更改本文档。
    :octicons-mark-github-16: [CodeInterpreterTool 源代码](https://github.com/aithoughts/aipmAI-tools/tree/zh/src/crewai_tools/tools/code_interpreter_tool)


## 描述
此工具用于使代理能够运行由代理本身生成的代码（Python3）。代码在沙盒环境中执行，因此运行任何代码都是安全的。

它非常有用，因为它允许代理生成代码，在相同的环境中运行它，获取结果并使用它来做出决策。

## 要求

- Docker

## 安装
安装 crewai_tools 包
```shell
pip install 'crewai[tools]'
```

## 示例

请记住，使用此工具时，代码必须由代理本身生成。代码必须是 Python3 代码。并且第一次运行需要一些时间，因为它需要构建 Docker 镜像。

```python
from crewai import Agent
from crewai_tools import CodeInterpreterTool

Agent(
    ...
    tools=[CodeInterpreterTool()],
)
```

我们还提供了一种直接从代理使用它的简单方法。

```python
from crewai import Agent

agent = Agent(
    ...
    allow_code_execution=True,
)
```
