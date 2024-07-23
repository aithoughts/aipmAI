---
title: 使用 LangChain 工具
description: 了解如何将 LangChain 工具与 CrewAI 代理集成，以增强基于搜索的查询等功能。
---

## 使用 LangChain 工具
!!! info "LangChain 集成"
    CrewAI 与 LangChain 用于基于搜索的查询等的综合工具包无缝集成，以下是 Langchain 提供的可用内置工具 [LangChain 工具包](https://python.langchain.com/docs/integrations/tools/)

```python
from crewai import Agent
from langchain.agents import Tool
from langchain.utilities import GoogleSerperAPIWrapper

# 设置 API 密钥
os.environ["SERPER_API_KEY"] = "您的密钥"

search = GoogleSerperAPIWrapper()

# 创建搜索工具并将其分配给代理
serper_tool = Tool(
  name="中间答案",
  func=search.run,
  description="对基于搜索的查询很有用",
)

agent = Agent(
  role='研究分析师',
  goal='提供最新的市场分析',
  backstory='一位对市场趋势有敏锐眼光的专家分析师。',
  tools=[serper_tool]
)

# 代码的其余部分...
```

## 结论
工具对于扩展 CrewAI 代理的功能至关重要，使其能够执行广泛的任务并有效协作。在使用 CrewAI 构建解决方案时，请利用自定义工具和现有工具来增强您的代理并增强 AI 生态系统。考虑利用错误处理、缓存机制和工具参数的灵活性来优化您的代理的性能和功能。
