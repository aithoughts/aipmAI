---
title: 使用 LlamaIndex 工具
description: 了解如何将 LlamaIndex 工具与 CrewAI 代理集成，以增强基于搜索的查询等功能。
---

## 使用 LlamaIndex 工具

!!! info "LlamaIndex 集成"
    CrewAI 与 LlamaIndex 用于 RAG（检索增强生成）和代理管道的综合工具包无缝集成，支持高级基于搜索的查询等功能。以下是 LlamaIndex 提供的可用内置工具。

```python
from crewai import Agent
from crewai_tools import LlamaIndexTool

# 示例 1：从 FunctionTool 初始化
from llama_index.core.tools import FunctionTool

your_python_function = lambda ...: ...
og_tool = FunctionTool.from_defaults(your_python_function, name="<名称>", description='<描述>')
tool = LlamaIndexTool.from_tool(og_tool)

# 示例 2：从 LlamaHub 工具初始化
from llama_index.tools.wolfram_alpha import WolframAlphaToolSpec
wolfram_spec = WolframAlphaToolSpec(app_id="<app_id>")
wolfram_tools = wolfram_spec.to_tool_list()
tools = [LlamaIndexTool.from_tool(t) for t in wolfram_tools]

# 示例 3：从 LlamaIndex 查询引擎初始化工具
query_engine = index.as_query_engine()
query_tool = LlamaIndexTool.from_query_engine(
    query_engine,
    name="Uber 2019 年 10K 查询工具",
    description="使用此工具查找 2019 年 Uber 10K 年度报告"
)

# 创建工具并将其分配给代理
agent = Agent(
  role='研究分析师',
  goal='提供最新的市场分析',
  backstory='一位对市场趋势有敏锐眼光的专家分析师。',
  tools=[tool, *tools, query_tool]
)

# 代码的其余部分...
```

## 入门步骤

要有效使用 LlamaIndexTool，请按照以下步骤操作：

1. **软件包安装**: 确认您的 Python 环境中已安装 `crewai[tools]` 软件包。

    ```shell
    pip install 'crewai[tools]'
    ```

2. **安装和使用 LlamaIndex**: 按照 LlamaIndex 文档 [LlamaIndex 文档](https://docs.llamaindex.ai/) 设置 RAG/代理管道。
