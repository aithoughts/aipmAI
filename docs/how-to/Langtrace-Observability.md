---
title: 使用 Langtrace 进行 CrewAI 代理监控
description: 如何使用外部可观察性工具 Langtrace 监控 CrewAI 代理的成本、延迟和性能。
---

# Langtrace 概述

Langtrace 是一款开源的外部工具，可帮助您为大型语言模型 (LLM)、LLM 框架和向量数据库设置可观察性和评估。虽然 Langtrace 不是直接内置于 CrewAI 中，但可以与 CrewAI 一起使用，以深入了解 CrewAI 代理的成本、延迟和性能。这种集成允许您记录超参数、监控性能下降，并建立持续改进代理的流程。

## 设置说明

1. 访问 [https://langtrace.ai/signup](https://langtrace.ai/signup) 注册 [Langtrace](https://langtrace.ai/)。
2. 创建一个项目并生成一个 API 密钥。
3. 使用以下命令在您的 CrewAI 项目中安装 Langtrace：

```bash
# 安装 SDK
pip install langtrace-python-sdk
```

## 在 CrewAI 中使用 Langtrace

要将 Langtrace 与您的 CrewAI 项目集成，请按照以下步骤操作：

1. 在脚本开头、任何 CrewAI 导入之前导入并初始化 Langtrace：

```python
from langtrace_python_sdk import langtrace
langtrace.init(api_key='<LANGTRACE_API_KEY>')

# 现在导入 CrewAI 模块
from crewai import Agent, Task, Crew
```

2. 照常创建您的 CrewAI 代理和任务。

3. 使用 Langtrace 的跟踪功能来监控您的 CrewAI 操作。例如：

```python
with langtrace.trace("CrewAI 任务执行"):
    result = crew.kickoff()
```

### 特性和它们在 CrewAI 中的应用

1. **LLM 令牌和成本跟踪**
   - 监控每个 CrewAI 代理交互的令牌使用情况和相关成本。
   - 例如：
     ```python
     with langtrace.trace("代理交互"):
         agent_response = agent.execute(task)
     ```

2. **执行步骤的跟踪图**
   - 可视化您的 CrewAI 任务的执行流程，包括延迟和日志。
   - 对于识别代理工作流程中的瓶颈很有用。

3. **使用手动注释进行数据集整理**
   - 从您的 CrewAI 任务输出创建数据集，用于未来的训练或评估。
   - 例如：
     ```python
     langtrace.log_dataset_item(task_input, agent_output, {"task_type": "research"})
     ```

4. **提示版本控制和管理**
   - 跟踪 CrewAI 代理中使用的不同版本的提示。
   - 对于 A/B 测试和优化代理性能很有用。

5. **带模型比较的提示游乐场**
   - 在部署之前测试和比较 CrewAI 代理的不同提示和模型。

6. **测试和评估**
   - 为您的 CrewAI 代理和任务设置自动化测试。
   - 例如：
     ```python
     langtrace.evaluate(agent_output, expected_output, "accuracy")
     ```

## 监控新的 CrewAI 功能

CrewAI 引入了一些可以使用 Langtrace 监控的新功能：

1. **代码执行**：监控代理执行的代码的性能和输出。
   ```python
   with langtrace.trace("代理代码执行"):
       code_output = agent.execute_code(code_snippet)
   ```

2. **第三方代理集成**：跟踪与 LlamaIndex、LangChain 和 Autogen 代理的交互。
