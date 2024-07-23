---
title: crewAI 代理
description: 什么是 crewAI 代理以及如何使用它们。
---

## 什么是代理？

!!! note "什么是代理？"
    代理是一个 **自主单元** ，被编程为：

    - 执行任务
    - 做出决定
    - 与其他代理进行沟通

    将代理视为团队中的一员，具有特定的技能和特定的工作要做。代理可以拥有不同的角色，例如“研究员”、“作家”或“客户支持”，每个角色都为团队的总体目标做出贡献。

## 代理属性

| 属性 | 参数  | 描述  |
| :--------------- | :---------------- |  :---------------- |
| **角色** | `role` | 定义代理在团队中的功能。它决定了代理最适合哪种任务。 | 
| **目标** | `goal` | 代理旨在实现的个人目标。它指导代理的决策过程。 | 
| **背景故事** | `backstory` | 提供代理角色和目标的上下文，丰富互动和协作动态。 | 
| **LLM**  | `llm` | 表示将运行代理的语言模型。它会动态地从 `OPENAI_MODEL_NAME` 环境变量中获取模型名称，如果未指定，则默认为“gpt-4”。 | 
| **工具**  | `tools` | 代理可以用来执行任务的功能或函数集。预期为与代理执行环境兼容的自定义类的实例。工具使用空列表的默认值进行初始化。 | 
| **函数调用 LLM** | `function_calling_llm` | 指定将为此代理处理工具调用的语言模型，如果传递，则覆盖 crew 函数调用 LLM。默认值为 `None`。 | 
| **最大迭代次数**  | `max_iter` | 最大迭代次数是代理在被迫给出最佳答案之前可以执行的最大迭代次数。默认值为 `25`。 | 
| **最大 RPM**  | `max_rpm` | 最大 RPM 是代理为避免速率限制而可以执行的每分钟最大请求数。它是可选的，可以不指定，默认值为 `None`。 | 
| **最大执行时间** | `max_execution_time` | 最大执行时间是代理执行任务的最长执行时间。它是可选的，可以不指定，默认值为 `None`，表示没有最大执行时间。 | 
| **详细** | `verbose` | 将此设置为 `True` 会将内部记录器配置为提供详细的执行日志，帮助调试和监控。默认值为 `False`。 | 
| **允许委派** | `allow_delegation` | 代理可以将任务或问题委派给彼此，确保每个任务都由最合适的代理处理。默认值为 `True`。 | 
| **步骤回调** | `step_callback` | 在代理的每个步骤之后调用的函数。这可用于记录代理的操作或执行其他操作。它将覆盖 crew `step_callback`。 | 
| **缓存** | `cache` | 指示代理是否应使用缓存来进行工具使用。默认值为 `True`。 | 
| **系统模板**  | `system_template`  | 指定代理的系统格式。默认值为 `None`。 | 
| **提示模板**  | `prompt_template`  | 指定代理的提示格式。默认值为 `None`。 | 
| **响应模板**  | `response_template`  | 指定代理的响应格式。默认值为 `None`。 | 


## 创建代理

!!! note "代理交互"
    代理可以使用 crewAI 的内置委派和通信机制相互交互。这允许在团队内进行动态任务管理和问题解决。

要创建代理，您通常需要使用所需的属性初始化 `Agent` 类的一个实例。这是一个包含所有属性的概念示例：

```python
# 示例：创建一个包含所有属性的代理
from crewai import Agent

agent = Agent(
  role='数据分析师',
  goal='提取可操作的见解',
  backstory="""您是一家大公司的数据分析师。
  您负责分析数据并为企业提供见解。
  您目前正在开展一个项目，以分析我们营销活动的绩效。""",
  tools=[my_tool1, my_tool2],  # 可选，默认为空列表
  llm=my_llm,  # 可选
  function_calling_llm=my_llm,  # 可选
  max_iter=15,  # 可选
  max_rpm=None, # 可选
  max_execution_time=None, # 可选
  verbose=True,  # 可选
  allow_delegation=True,  # 可选
  step_callback=my_intermediate_step_callback,  # 可选
  cache=True,  # 可选
  system_template=my_system_template,  # 可选
  prompt_template=my_prompt_template,  # 可选
  response_template=my_response_template,  # 可选
  config=my_config,  # 可选
  crew=my_crew,  # 可选
  tools_handler=my_tools_handler,  # 可选
  cache_handler=my_cache_handler,  # 可选
  callbacks=[callback1, callback2],  # 可选
  agent_executor=my_agent_executor  # 可选
)
```

## 设置提示模板

提示模板用于格式化代理的提示。您可以使用它来更新代理的系统、常规和响应模板。以下是如何设置提示模板的示例：

```python
agent = Agent(
    role="{topic} 专家",
    goal="找出 {goal}",
    backstory="我是 {role} 大师",
    system_template="""<|start_header_id|>system<|end_header_id|>{{ .System }}<|eot_id|>""",
    prompt_template="""<|start_header_id|>user<|end_header_id|>{{ .Prompt }}<|eot_id|>""",
    response_template="""<|start_header_id|>assistant<|end_header_id|>{{ .Response }}<|eot_id|>""",
)
```

## 引入您的第三方代理

!!! note "使用 crewai 的 BaseAgent 类扩展您的第三方代理，例如 LlamaIndex、Langchain、Autogen 或完全自定义的代理。"

    BaseAgent 包括与您的团队集成所需，以便在您自己的团队中运行任务并将任务委派给其他代理的属性和方法。

    CrewAI 是一个通用的多代理框架，允许所有代理协同工作以自动化任务和解决问题。

```py
from crewai import Agent, Task, Crew
from custom_agent import CustomAgent # 您需要使用 CrewAI BaseAgent 类构建和扩展您自己的代理逻辑，然后在此处导入。

from langchain.agents import load_tools

langchain_tools = load_tools(["google-serper"], llm=llm)

agent1 = CustomAgent(
    role="背景故事代理",
    goal="谁是 {input}？",
    backstory="代理背景故事",
    verbose=True,
)

task1 = Task(
    expected_output="{input} 的简短传记",
    description="{input} 的简短传记",
    agent=agent1,
)

agent2 = Agent(
    role="传记代理",
    goal="总结 {input} 的简短传记，如果需要，请进行更多研究",
    backstory="代理背景故事",
    verbose=True,
)

task2 = Task(
    description="简短传记的 tldr 摘要",
    expected_output="传记的 5 个要点摘要",
    agent=agent2,
    context=[task1],
)

my_crew = Crew(agents=[agent1, agent2], tasks=[task1, task2])
crew = my_crew.kickoff(inputs={"input": "莫言"})
```

## 结论

代理是 CrewAI 框架的构建块。通过了解如何定义代理以及如何与代理交互，您可以创建利用协作智能的力量来构建复杂的 AI 系统。
