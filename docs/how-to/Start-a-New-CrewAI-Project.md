---
title: 启动新的 CrewAI 项目
description: 启动新的 CrewAI 项目的综合指南，包括最新的更新和项目设置方法。
---

# 启动您的 CrewAI 项目

欢迎阅读启动新 CrewAI 项目的终极指南。本文档将指导您完成创建、自定义和运行 CrewAI 项目的步骤，确保您拥有入门所需的一切。

## 先决条件

我们假设您已经安装了 CrewAI。如果没有，请参阅 [安装指南](https://aipmai.theforage.cn/how-to/Installing-CrewAI/) 来安装 CrewAI 及其依赖项。

## 创建新项目

要创建新项目，请运行以下 CLI 命令：

```shell
$ crewai create <project_name>
```

此命令将创建一个具有以下结构的新项目文件夹：

```shell
my_project/
├── .gitignore
├── pyproject.toml
├── README.md
└── src/
    └── my_project/
        ├── __init__.py
        ├── main.py
        ├── crew.py
        ├── tools/
        │   ├── custom_tool.py
        │   └── __init__.py
        └── config/
            ├── agents.yaml
            └── tasks.yaml
```

您现在可以通过编辑 `src/my_project` 文件夹中的文件来开始开发您的项目。`main.py` 文件是您项目的入口点，`crew.py` 文件是您定义代理和任务的地方。

## 自定义您的项目

要自定义您的项目，您可以：
- 修改 `src/my_project/config/agents.yaml` 来定义您的代理。
- 修改 `src/my_project/config/tasks.yaml` 来定义您的任务。
- 修改 `src/my_project/crew.py` 以添加您自己的逻辑、工具和特定参数。
- 修改 `src/my_project/main.py` 以添加代理和任务的自定义输入。
- 将您的环境变量添加到 `.env` 文件中。

### 示例：定义代理和任务

#### agents.yaml

```yaml
researcher:
  role: >
    求职者研究员
  goal: >
    寻找该职位的潜在候选人
  backstory: >
    您擅长通过探索各种在线资源来寻找合适的候选人。您识别合适候选人的技能可确保与职位最匹配。
```

#### tasks.yaml

```yaml
research_candidates_task:
  description: >
    进行彻底的研究以找到指定职位的潜在候选人。
    利用各种在线资源和数据库来收集潜在候选人的完整列表。
    确保候选人符合提供的职位要求。

    职位要求：
    {job_requirements}
  expected_output: >
    一份包含 10 个潜在候选人的列表，其中包含他们的联系方式和突出显示其适合性的简要资料。
  agent: researcher # 这需要与 AGENTS.YAML 文件中的代理名称以及 Crew.PY 文件中定义的代理相匹配
  context: # 这些需要与上面定义的任务名称以及 TASKS.YAML 文件和 Crew.PY 文件中定义的任务相匹配
    - researcher
```

### 引用变量：
将使用您定义的同名函数。例如，您可以从 task.yaml 文件中引用特定任务的代理。确保您注释的代理和函数名称相同，否则您的任务将无法正确识别引用。

#### 引用示例
agent.yaml
```yaml
email_summarizer:
    role: >
      邮件摘要器
    goal: >
      将电子邮件汇总成简洁明了的摘要
    backstory: >
      您将创建一份包含 5 个要点摘要的报告
    llm: mixtal_llm
```

task.yaml
```yaml
email_summarizer_task:
    description: >
      将电子邮件汇总成 5 个要点
    expected_output: >
      包含 5 个要点的电子邮件摘要
    agent: email_summarizer
    context:
      - reporting_task
      - research_task
```

使用注释可以正确引用 crew.py 文件中的代理和任务。

### 注释包括：
* @agent
* @task
* @crew
* @llm
* @tool
* @callback
* @output_json
* @output_pydantic
* @cache_handler


crew.py
```py
...
    @llm
    def mixtal_llm(self):
        return ChatGroq(temperature=0, model_name="mixtral-8x7b-32768")

    @agent
    def email_summarizer(self) -> Agent:
        return Agent(
            config=self.agents_config["email_summarizer"],
        )
    ## ...定义的其他任务
    @task
    def email_summarizer_task(self) -> Task:
        return Task(
            config=self.tasks_config["email_summarizer_task"],
        )
...
```



## 安装依赖项

要安装项目的依赖项，您可以使用 Poetry。首先，导航到您的项目目录：

```shell
$ cd my_project
$ poetry lock
$ poetry install
```

这将安装 `pyproject.toml` 文件中指定的依赖项。

## 插值变量

在您的 `agents.yaml` 和 `tasks.yaml` 文件中插入的任何变量（如 `{variable}`）都将替换为 `main.py` 文件中该变量的值。

#### agents.yaml

```yaml
research_task:
  description: >
    在 {customer_domain} 的背景下，对客户和竞争对手进行彻底的研究。
    确保您找到任何有趣且相关的信息，因为当前年份是 2024 年。
  expected_output: >
    关于客户及其客户和竞争对手的完整报告，
    包括他们的人口统计、偏好、市场定位和受众参与度。
```

#### main.py

```python
# main.py
def run():
    inputs = {
        "customer_domain": "crewai.com"
    }
    MyProjectCrew(inputs).crew().kickoff(inputs=inputs)
```

## 运行您的项目

要运行您的项目，请使用以下命令：

```shell
$ poetry run my_project
```

这将初始化您的 AI 代理团队，并开始执行 `main.py` 文件中配置中定义的任务。

## 部署您的项目

部署您的团队的最简单方法是通过 [CrewAI+](https://www.crewai.com/crewaiplus)，您只需点击几下即可部署您的团队。
