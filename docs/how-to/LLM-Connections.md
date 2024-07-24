---
title: 将 CrewAI 连接到 LLM
description: 有关将 CrewAI 与各种大型语言模型 (LLM) 集成的综合指南，包括详细的类属性、方法和配置选项。
---

## 将 CrewAI 连接到 LLM

!!! note "默认 LLM"
    默认情况下，CrewAI 使用 OpenAI 的 GPT-4 模型（具体来说，是由 OPENAI_MODEL_NAME 环境变量指定的模型，默认为“gpt-4o”）进行语言处理。您可以按照本指南中的说明配置您的代理以使用不同的模型或 API。

CrewAI 提供了连接到各种 LLM 的灵活性，包括通过 [Ollama](https://ollama.ai) 连接到本地模型以及连接到 Azure 等不同的 API。它与所有 [LangChain LLM](https://python.langchain.com/docs/integrations/llms/) 组件兼容，支持各种集成以实现定制的 AI 解决方案。

## CrewAI 代理概述

`Agent` 类是在 CrewAI 中实现 AI 解决方案的基石。以下是 Agent 类属性和方法的全面概述：

- **属性**：
    - `role`：定义代理在解决方案中的角色。
    - `goal`：指定代理的目标。
    - `backstory`：提供代理的背景故事。
    - `cache` *可选*：确定代理是否应使用缓存来存储工具使用情况。默认为 `True`。
    - `max_rpm` *可选*：代理执行应遵循的每分钟最大请求数。可选。
    - `verbose` *可选*：启用代理执行的详细日志记录。默认为 `False`。
    - `allow_delegation` *可选*：允许代理将任务委派给其他代理，默认为 `True`。
    - `tools`：指定代理可用于执行任务的工具。可选。
    - `max_iter` *可选*：代理执行任务的最大迭代次数，默认为 25。
    - `max_execution_time` *可选*：代理执行任务的最长时间。可选。
    - `step_callback` *可选*：提供在每个步骤后执行的回调函数。可选。
    - `llm` *可选*：指示代理使用的大型语言模型。默认情况下，它使用环境变量“OPENAI_MODEL_NAME”中定义的 GPT-4 模型。
    - `function_calling_llm` *可选*：将把 ReAct CrewAI 代理变成函数调用代理。
    - `callbacks` *可选*：LangChain 库中的一系列回调函数，在代理的执行过程中触发。
    - `system_template` *可选*：用于定义代理系统格式的可选字符串。
    - `prompt_template` *可选*：用于定义代理提示格式的可选字符串。
    - `response_template` *可选*：用于定义代理响应格式的可选字符串。

```python
# 必填
os.environ["OPENAI_MODEL_NAME"]="gpt-4-0125-preview"

# 代理将自动使用环境变量中定义的模型
example_agent = Agent(
  role='当地专家',
  goal='提供有关城市的见解',
  backstory="知识渊博的当地导游。",
  verbose=True
)
```

## Ollama 集成
Ollama 是本地 LLM 集成的首选，它提供了自定义和隐私优势。要将 Ollama 与 CrewAI 集成，请设置适当的环境变量，如下所示。

### 设置 Ollama
- **环境变量配置**：要集成 Ollama，请设置以下环境变量：
```sh
OPENAI_API_BASE='http://localhost:11434'
OPENAI_MODEL_NAME='llama2'  # 根据可用模型进行调整
OPENAI_API_KEY=''
```

## Ollama 集成（例如，在本地使用 Llama 2）
1. [下载 Ollama](https://ollama.com/download)。
2. 设置好 Ollama 后，在终端中输入以下行来拉取 Llama2 ```ollama pull llama2```。
3. 享受由 crewai 的优秀代理提供支持的免费 Llama2 模型。
```python
from crewai import Agent, Task, Crew
from langchain.llms import Ollama
import os
os.environ["OPENAI_API_KEY"] = "NA"

llm = Ollama(
    model = "llama2",
    base_url = "http://localhost:11434")

general_agent = Agent(role = "数学教授",
                      goal = """为提出数学问题的学生提供解决方案并给出答案。""",
                      backstory = """您是一位优秀的数学教授，喜欢以每个人都能理解您的解决方案的方式解决数学问题""",
                      allow_delegation = False,
                      verbose = True,
                      llm = llm)

task = Task(description="""3 + 5 等于多少""",
             agent = general_agent,
             expected_output="一个数字答案。")

crew = Crew(
            agents=[general_agent],
            tasks=[task],
            verbose=2
        )

result = crew.kickoff()

print(result)
```

## HuggingFace 集成
您可以通过几种不同的方式使用 HuggingFace 来托管您的 LLM。

### 您自己的 HuggingFace 端点
```python
from langchain_community.llms import HuggingFaceEndpoint

llm = HuggingFaceEndpoint(
    endpoint_url="<您的端点 URL>",
    huggingfacehub_api_token="<HF 令牌>",
    task="text-generation",
    max_new_tokens=512
)

agent = Agent(
    role="HuggingFace 代理",
    goal="使用 HuggingFace 生成文本",
    backstory="GitHub 文档的勤奋探索者。",
    llm=llm
)
```

### 来自 HuggingFaceHub 端点
```python
from langchain_community.llms import HuggingFaceHub

llm = HuggingFaceHub(
    repo_id="HuggingFaceH4/zephyr-7b-beta",
    huggingfacehub_api_token="<HF 令牌>",
    task="text-generation",
)
```

## 与 OpenAI 兼容的 API 端点
使用环境变量在 API 和模型之间无缝切换，支持 FastChat、LM Studio、Groq 和 Mistral AI 等平台。

### 配置示例
#### FastChat
```sh
OPENAI_API_BASE="http://localhost:8001/v1"
OPENAI_MODEL_NAME='oh-2.5m7b-q51'
OPENAI_API_KEY=NA
```

#### LM Studio
启动 [LM Studio](https://lmstudio.ai) 并转到“服务器”选项卡。然后从下拉菜单中选择一个模型并等待它加载。加载完成后，单击绿色的“启动服务器”按钮，然后使用显示的 URL、端口和 API 密钥（您可以修改它们）。以下是截至 LM Studio 0.2.19 的默认设置示例：
```sh
OPENAI_API_BASE="http://localhost:1234/v1"
OPENAI_API_KEY="lm-studio"
```

#### Groq API
```sh
OPENAI_API_KEY=your-groq-api-key
OPENAI_MODEL_NAME='llama3-8b-8192'
OPENAI_API_BASE=https://api.groq.com/openai/v1
```

#### Mistral API
```sh
OPENAI_API_KEY=your-mistral-api-key
OPENAI_API_BASE=https://api.mistral.ai/v1
OPENAI_MODEL_NAME="mistral-small"
```

### Solar
```python
from langchain_community.chat_models.solar import SolarChat
# 初始化语言模型
os.environ["SOLAR_API_KEY"] = "your-solar-api-key"
llm = SolarChat(max_tokens=1024)

# 免费开发者 API 密钥可在此处获取：https://console.upstage.ai/services/solar
# Langchain 示例：https://github.com/langchain-ai/langchain/pull/18556
```

### text-gen-web-ui
```sh
OPENAI_API_BASE=http://localhost:5000/v1
OPENAI_MODEL_NAME=NA
OPENAI_API_KEY=NA
```

### Cohere
```python
from langchain_cohere import ChatCohere
# 初始化语言模型
os.environ["COHERE_API_KEY"] = "your-cohere-api-key"
llm = ChatCohere()

# 免费开发者 API 密钥可在此处获取：https://cohere.com/
# Langchain 文档：https://python.langchain.com/docs/integrations/chat/cohere
```

### Azure Open AI 配置
对于 Azure OpenAI API 集成，请设置以下环境变量：
```sh
AZURE_OPENAI_VERSION="2022-12-01"
AZURE_OPENAI_DEPLOYMENT=""
AZURE_OPENAI_ENDPOINT=""
AZURE_OPENAI_KEY=""
```

### 使用 Azure LLM 的示例代理
```python
from dotenv import load_dotenv
from crewai import Agent
from langchain_openai import AzureChatOpenAI

load_dotenv()

azure_llm = AzureChatOpenAI(
    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
    api_key=os.environ.get("AZURE_OPENAI_KEY")
)

azure_agent = Agent(
  role='示例代理',
  goal='演示自定义 LLM 配置',
  backstory='GitHub 文档的勤奋探索者。',
  llm=azure_llm
)
```

## 结论
将 CrewAI 与不同的 LLM 集成扩展了该框架的多功能性，允许跨各种域和平台实现定制的、高效的 AI 解决方案。
