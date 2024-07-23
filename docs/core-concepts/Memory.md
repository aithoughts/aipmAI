---
title：aipmAI Memory 系统
description：利用 aipmAI 框架中的Memory 系统来增强代理功能。
---

## aipmAI 中的Memory 系统简介
!!! note "增强代理智能"
    aipmAI 框架引入了一个复杂的 Memory 系统，旨在显著增强 AI 代理的功能。该系统包括短期记忆、长期记忆、实体记忆和上下文记忆，它们各自在帮助代理记住、推理和从过去的交互中学习方面发挥着独特的作用。

## Memory 系统组件

| 组件            | 描述                                                  |
| :------------------- | :----------------------------------------------------------- |
| **短期记忆**| 临时存储最近的交互和结果，使代理能够在当前执行期间回忆和利用与其当前上下文相关的信息。 |
| **长期记忆** | 保存过去执行中宝贵的见解和学习成果，使代理能够随着时间的推移建立和完善其知识。因此，代理可以记住他们在多次执行中做对了什么，做错了什么。 |
| **实体记忆**    | 捕获和组织在任务期间遇到的实体（人、地点、概念）的信息，促进更深入的理解和关系映射。 |
| **上下文记忆**| 通过组合“短期记忆”、“长期记忆”和“实体记忆”来维护交互的上下文，帮助代理在一系列任务或对话中保持一致性和相关性。 |

## Memory 系统如何增强代理

1. **上下文感知**：借助短期记忆和上下文记忆，代理能够在对话或任务序列中保持上下文，从而做出更一致和更相关的响应。

2. **经验积累**：长期记忆允许代理积累经验，从过去的行动中学习，以改进未来的决策和问题解决。

3. **实体理解**：通过维护实体记忆，代理可以识别和记住关键实体，增强其处理和交互复杂信息的能力。

## 在您的 Crew 中实现Memory

在配置 crew 时，您可以启用和自定义每个Memory组件，以适应 crew 的目标及其将执行的任务的性质。
默认情况下，Memory 系统是禁用的，您可以通过在 crew 配置中设置 `memory=True` 来确保它是活动的。默认情况下，Memory将使用 OpenAI Embeddings，但您可以通过将 `embedder` 设置为不同的模型来更改它。

'embedder' 仅适用于使用 Chroma for RAG 和 EmbedChain 包的 **短期记忆**。
**长期记忆** 使用 SQLLite3 来存储任务结果。目前，还没有办法覆盖这些存储实现。
数据存储文件被保存到使用 appdirs 包找到的平台特定位置，项目的名称可以使用 **AIPMAI_STORAGE_DIR** 环境变量覆盖。

### 示例：为 Crew 配置Memory

```python
from crewAI import Crew, Agent, Task, Process

# 组装具有Memory功能的 crew
my_crew = Crew(
    agents=[...],
    tasks=[...],
    process=Process.sequential,
    memory=True,
    verbose=True
)
```

## 其他嵌入提供程序

### 使用 OpenAI 嵌入（已经是默认设置）
```python
from crewAI import Crew, Agent, Task, Process

my_crew = Crew(
		agents=[...],
		tasks=[...],
		process=Process.sequential,
		memory=True,
		verbose=True,
		embedder={
				"provider": "openai",
				"config":{
						"model": 'text-embedding-3-small'
				}
		}
)
```

### 使用 Google AI 嵌入
```python
from crewAI import Crew, Agent, Task, Process

my_crew = Crew(
		agents=[...],
		tasks=[...],
		process=Process.sequential,
		memory=True,
		verbose=True,
		embedder={
			"provider": "google",
			"config":{
				"model": 'models/embedding-001',
				"task_type": "retrieval_document",
				"title": "Embeddings for Embedchain"
			}
		}
)
```

### 使用 Azure OpenAI 嵌入
```python
from crewAI import Crew, Agent, Task, Process

my_crew = Crew(
		agents=[...],
		tasks=[...],
		process=Process.sequential,
		memory=True,
		verbose=True,
		embedder={
			"provider": "azure_openai",
			"config":{
				"model": 'text-embedding-ada-002',
				"deployment_name": "you_embedding_model_deployment_name"
			}
		}
)
```

### 使用 GPT4ALL 嵌入
```python
from crewAI import Crew, Agent, Task, Process

my_crew = Crew(
		agents=[...],
		tasks=[...],
		process=Process.sequential,
		memory=True,
		verbose=True,
		embedder={
			"provider": "gpt4all"
		}
)
```

### 使用 Vertex AI 嵌入
```python
from crewAI import Crew, Agent, Task, Process

my_crew = Crew(
		agents=[...],
		tasks=[...],
		process=Process.sequential,
		memory=True,
		verbose=True,
		embedder={
			"provider": "vertexai",
			"config":{
				"model": 'textembedding-gecko'
			}
		}
)
```

### 使用 Cohere 嵌入
```python
from crewAI import Crew, Agent, Task, Process

my_crew = Crew(
		agents=[...],
		tasks=[...],
		process=Process.sequential,
		memory=True,
		verbose=True,
		embedder={
			"provider": "cohere",
			"config":{
				"model": "embed-english-v3.0"
    		"vector_dimension": 1024
			}
		}
)
```

### 重置Memory
```sh
aipmAI reset_memories [OPTIONS]
```

#### 重置Memory选项
- **`-l, --long`**
  - **描述:** 重置长期记忆。
  - **类型:** 标志（布尔值）
  - **默认值:** False

- **`-s, --short`**
  - **描述:** 重置短期记忆。
  - **类型:** 标志（布尔值）
  - **默认值:** False

- **`-e, --entities`**
  - **描述:** 重置实体记忆。
  - **类型:** 标志（布尔值）
  - **默认值:** False

- **`-k, --kickoff-outputs`**
  - **描述:** 重置最新的启动任务输出。
  - **类型:** 标志（布尔值）
  - **默认值:** False

- **`-a, --all`**
  - **描述:** 重置所有记忆。
  - **类型:** 标志（布尔值）
  - **默认值:** False



## 使用 aipmAI Memory 系统的优势
- **自适应学习**：Crew 随着时间的推移变得更加高效，适应新信息并改进其处理任务的方法。
- **增强个性化**：Memory使代理能够记住用户偏好和历史交互，从而带来个性化的体验。
- **改进问题解决**：访问丰富的Memory存储可帮助代理做出更明智的决策，利用过去的学习成果和上下文见解。

## 入门
将 aipmAI 的Memory 系统集成到您的项目中非常简单。通过利用提供的Memory组件和配置，您可以快速赋予您的代理记忆、推理和从交互中学习的能力，从而解锁新的智能和能力水平。
