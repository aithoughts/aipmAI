---
title: 在 crewAI 中创建和使用工具
description: 关于在 crewAI 框架内创建、使用和管理自定义工具的综合指南，包括新功能和错误处理。
---

## 在 crewAI 中创建和使用工具
本指南提供了有关为 crewAI 框架创建自定义工具以及如何有效管理和利用这些工具的详细说明，其中包含了工具委托、错误处理和动态工具调用等最新功能。它还强调了协作工具的重要性，使代理能够执行各种操作。

### 先决条件
在创建您自己的工具之前，请确保您已安装 crewAI 额外工具包：

```bash
pip install 'crewai[tools]'
```

### 子类化 `BaseTool`

要创建个性化工具，请继承 `BaseTool` 并定义必要的属性和 `_run` 方法。

```python
from crewai_tools import BaseTool

class MyCustomTool(BaseTool):
    name: str = "我的工具的名称"
    description: str = "此工具的作用。这对于有效利用至关重要。"

    def _run(self, argument: str) -> str:
        # 您的工具逻辑
        return "工具的结果"
```

### 使用 `tool` 装饰器

或者，使用 `tool` 装饰器直接创建工具。这需要在函数中指定属性和工具的逻辑。

```python
from crewai_tools import tool

@tool("工具名称")
def my_simple_tool(question: str) -> str:
    """工具描述，以提高清晰度。"""
    # 工具逻辑
    return "工具输出"
```

### 为工具定义缓存函数

要使用缓存优化工具性能，请使用 `cache_function` 属性定义自定义缓存策略。

```python
@tool("带缓存的工具")
def cached_tool(argument: str) -> str:
    """工具功能描述。"""
    return "可缓存的结果"

def my_cache_strategy(arguments: dict, result: str) -> bool:
    # 定义自定义缓存逻辑
    return True if some_condition else False

cached_tool.cache_function = my_cache_strategy
```

通过遵循这些准则并将新功能和协作工具纳入您的工具创建和管理流程中，您可以充分利用 crewAI 框架的功能，从而增强开发体验和 AI 代理的效率。
