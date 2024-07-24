---
title: 执行过程中的人工输入
description: 在复杂决策过程中将 CrewAI 与人工输入相结合，并充分利用代理属性和工具的功能。
---

# 代理执行中的人工输入

在代理执行的几种情况下，人工输入至关重要，它允许代理在必要时请求更多信息或澄清。此功能在复杂决策过程或代理需要更多细节才能有效完成任务时特别有用。

## 在 CrewAI 中使用人工输入

要将人工输入集成到代理执行中，请在任务定义中设置 `human_input` 标志。启用后，代理会在给出最终答案之前提示用户输入。此输入可以提供额外的上下文、澄清歧义或验证代理的输出。

### 示例

```shell
pip install crewai
```

```python
import os
from crewai import Agent, Task, Crew
from crewai_tools import SerperDevTool

os.environ["SERPER_API_KEY"] = "您的密钥"  # serper.dev API 密钥
os.environ["OPENAI_API_KEY"] = "您的密钥"

# 加载工具
search_tool = SerperDevTool()

# 使用角色、目标、工具和其他属性定义您的代理
researcher = Agent(
    role='高级研究分析师',
    goal='发现人工智能和数据科学领域的尖端发展',
    backstory=(
        "您是一家领先科技智库的高级研究分析师。"
        "您的专长在于识别人工智能和数据科学领域的新兴趋势和技术。"
        "您具有剖析复杂数据和提出可操作见解的诀窍。"
    ),
    verbose=True,
    allow_delegation=False,
    tools=[search_tool]
)
writer = Agent(
    role='科技内容策略师',
    goal='制作关于技术进步的引人入胜的内容',
    backstory=(
        "您是一位著名的科技内容策略师，以您对技术和创新的深刻见解和引人入胜的文章而闻名。"
        "凭借对科技行业的深入了解，您将复杂的概念转化为引人入胜的叙述。"
    ),
    verbose=True,
    allow_delegation=True,
    tools=[search_tool],
    cache=False,  # 禁用此代理的缓存
)

# 为您的代理创建任务
task1 = Task(
    description=(
        "对 2024 年人工智能的最新进展进行全面分析。"
        "确定关键趋势、突破性技术和潜在的行业影响。"
        "将您的发现汇编成一份详细的报告。"
        "在最终确定答案之前，请务必与人工核实草稿是否合格。"
    ),
    expected_output='一份关于 2024 年人工智能最新进展的完整报告，不要遗漏任何内容',
    agent=researcher,
    human_input=True
)

task2 = Task(
    description=(
        "利用研究人员报告中的见解，撰写一篇引人入胜的博客文章，重点介绍最重大的 AI 进展。"
        "您的文章应该内容丰富且通俗易懂，以满足精通技术的受众的需求。"
        "力求以一种捕捉这些突破的本质及其对未来影响的方式进行叙述。"
    ),
    expected_output='一篇关于 2024 年人工智能最新进展的引人入胜的 3 段博客文章，格式为 markdown',
    agent=writer
)

# 使用顺序流程实例化您的团队
crew = Crew(
    agents=[researcher, writer],
    tasks=[task1, task2],
    verbose=2,
    memory=True,
)

# 让您的团队开始工作！
result = crew.kickoff()

print("######################")
print(result)
```
