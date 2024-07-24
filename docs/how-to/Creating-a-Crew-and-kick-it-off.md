---
title: 组建和激活您的 CrewAI 团队
description: 为您的项目创建动态 CrewAI 团队的综合指南，更新的功能包括详细模式、记忆能力、异步执行、输出定制、语言模型配置、代码执行、与第三方代理集成以及改进的任务管理。
---

## 简介
通过设置您的环境并使用最新功能启动您的 AI 团队，开始您的 CrewAI 之旅。本指南确保顺利开始，并结合所有最新更新以获得增强的体验，包括代码执行功能、与第三方代理集成以及高级任务管理。

## 第 0 步：安装
安装 CrewAI 和您的项目所需的任何软件包。CrewAI 与 Python >=3.10,<=3.13 兼容。

```shell
pip install crewai
pip install 'crewai[tools]'
```

## 第 1 步：组建您的代理
使用不同的角色、背景故事和增强功能定义您的代理。Agent 类现在支持广泛的属性，用于微调对代理行为和交互的控制，包括代码执行和与第三方代理集成。

```python
import os
from langchain.llms import OpenAI
from crewai import Agent
from crewai_tools import SerperDevTool, BrowserbaseLoadTool, EXASearchTool

os.environ["OPENAI_API_KEY"] = "Your OpenAI Key"
os.environ["SERPER_API_KEY"] = "Your Serper Key"
os.environ["BROWSERBASE_API_KEY"] = "Your BrowserBase Key"
os.environ["BROWSERBASE_PROJECT_ID"] = "Your BrowserBase Project Id"

search_tool = SerperDevTool()
browser_tool = BrowserbaseLoadTool()
exa_search_tool = EXASearchTool()

# 创建具有高级配置的高级研究员代理
researcher = Agent(
    role='高级研究员',
    goal='发现 {topic} 中的突破性技术',
    backstory=("在好奇心的驱使下，您处于创新的最前沿， "
               "渴望探索和分享可以改变世界的知识。"),
    memory=True,
    verbose=True,
    allow_delegation=False,
    tools=[search_tool, browser_tool],
    allow_code_execution=False,  # 用于启用代码执行的新属性
    max_iter=15,  # 任务执行的最大迭代次数
    max_rpm=100,  # 每分钟最大请求数
    max_execution_time=3600,  # 最大执行时间（以秒为单位）
    system_template="您的自定义系统模板",  # 自定义系统模板
    prompt_template="您的自定义提示模板",  # 自定义提示模板
    response_template="您的自定义响应模板",  # 自定义响应模板
)

# 创建具有自定义工具和特定配置的作者代理
writer = Agent(
    role='作者',
    goal='讲述关于 {topic} 的引人入胜的技术故事',
    backstory=("凭借简化复杂主题的才能，您精心制作引人入胜的 "
               "叙述，以吸引和教育，将新发现公之于众。"),
    verbose=True,
    allow_delegation=False,
    memory=True,
    tools=[exa_search_tool],
    function_calling_llm=OpenAI(model_name="gpt-3.5-turbo"),  # 用于函数调用的单独 LLM
)

# 设置特定的经理代理
manager = Agent(
  role='经理',
  goal='确保团队的顺利运作和协调',
  verbose=True,
  backstory=(
    "作为一名经验丰富的项目经理，您擅长组织 "
    "任务、管理时间线并确保团队按计划进行。"
  ),
  allow_code_execution=True,  # 为经理启用代码执行
)
```

### 新的代理属性和功能

1. `allow_code_execution`：启用或禁用代理的代码执行功能（默认为 False）。
2. `max_execution_time`：设置代理完成任务的最大执行时间（以秒为单位）。
3. `function_calling_llm`：指定用于函数调用的单独语言模型。
