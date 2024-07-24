---
title: 从最近一次 Crew 启动中重放任务
description: 从最近一次 crew.kickoff(...) 中重放任务
---

## 简介
CrewAI 提供了从最近一次 Crew 启动中指定的任务开始重放的功能。当您完成一次启动后，可能希望重试某些任务，或者不需要重新获取数据，并且您的代理已经从启动执行中保存了上下文，您只需要重放所需的任务时，此功能特别有用。

## 注意
您必须先运行 `crew.kickoff()`，然后才能重放任务。目前，仅支持最近一次启动，因此如果您使用 `kickoff_for_each`，它将只允许您从最近一次 Crew 运行中重放。

以下是重放任务的示例：

### 使用 CLI 从特定任务开始重放
要使用重放功能，请执行以下步骤：

1. 打开您的终端或命令提示符。
2. 导航到您的 CrewAI 项目所在的目录。
3. 运行以下命令：

要查看最近一次启动的 task_id，请使用：
```shell
crewai log-tasks-outputs
```

获得要重放的 task_id 后，请使用：
```shell
crewai replay -t <task_id>
```


### 以编程方式从任务开始重放
要以编程方式从任务开始重放，请使用以下步骤：

1. 为重放过程指定 task_id 和输入参数。
2. 在 try-except 块中执行 replay 命令以处理潜在的错误。

```python
   def replay():
    """
    从特定任务开始重放 Crew 执行。
    """
    task_id = '<task_id>'
    inputs = {"topic": "CrewAI Training"} # 这是可选的，您可以传入要重放的输入，否则将使用先前启动的输入
    try:
        YourCrewName_Crew().crew().replay(task_id=task_id, inputs=inputs)

    except Exception as e:
        raise Exception(f"重放 Crew 时发生错误：{e}")
```
