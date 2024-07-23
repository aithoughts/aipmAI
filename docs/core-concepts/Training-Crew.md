---
title: crewAI 训练
description: 了解如何通过尽早提供反馈来训练您的 crewAI 代理，并获得一致的结果。
---

## 简介
CrewAI 中的训练功能允许您使用命令行界面 (CLI) 训练您的 AI 代理。通过运行命令 `crewai train -n <n_iterations>`，您可以指定训练过程的迭代次数。

在训练期间，CrewAI 利用各种技术来优化您的代理的性能以及人类反馈。这有助于代理提高他们的理解力、决策能力和解决问题的能力。

### 使用 CLI 训练您的 Crew
要使用训练功能，请按照以下步骤操作：

1. 打开您的终端或命令提示符。
2. 导航到您的 CrewAI 项目所在的目录。
3. 运行以下命令：

```shell
crewai train -n <n_iterations>
```

### 以编程方式训练您的 Crew
要以编程方式训练您的 crew，请使用以下步骤：

1. 定义训练的迭代次数。
2. 指定训练过程的输入参数。
3. 在 try-except 块中执行训练命令以处理潜在的错误。

```python
    n_iterations = 2
    inputs = {"topic": "CrewAI Training"}

    try:
        YourCrewName_Crew().crew().train(n_iterations= n_iterations, inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")
```

!!! note "将 `<n_iterations>` 替换为所需的训练迭代次数。这决定了代理将经历多少次训练过程。"


### 需要注意的关键点：
- **正整数要求：** 确保迭代次数 (`n_iterations`) 是一个正整数。如果不满足此条件，代码将引发 `ValueError`。
- **错误处理：** 代码处理子进程错误和意外异常，向用户提供错误消息。

需要注意的是，训练过程可能需要一些时间，具体取决于您的代理的复杂性，并且还需要您在每次迭代中提供反馈。

训练完成后，您的代理将具备增强的能力和知识，准备好应对复杂的任务并提供更加一致和有价值的见解。

请记住定期更新和重新训练您的代理，以确保它们与该领域的最新信息和进步保持同步。

祝您在 CrewAI 中训练愉快！
