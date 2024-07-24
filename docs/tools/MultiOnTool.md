## MultiOnTool 文档

!!! note "实验性"
    我们仍在努力改进工具，因此未来可能会更改本文档。
    :octicons-mark-github-16: [MultiOnTool 源代码](https://github.com/aithoughts/aipmAI-tools/tree/zh/src/crewai_tools/tools/multion_tool)

## 描述

MultiOnTool 集成在 crewai_tools 软件包中，使 CrewAI 代理能够通过自然语言指令浏览网页并与之交互。该工具利用 Multion API，促进了无缝网页浏览，使其成为需要动态网页数据交互项目的必备资产。

## 安装

要使用 MultiOnTool，请确保在您的环境中安装了 `crewai[tools]` 软件包。如果尚未安装，可以使用以下命令添加：
```shell
pip install 'crewai[tools]'
```

## 示例

以下示例演示了如何初始化该工具并使用给定查询执行搜索：

```python
from crewai import Agent, Task, Crew
from crewai_tools import MultiOnTool

# 从 MultiOn 工具初始化工具
multion_tool = MultiOnTool(api_key= "YOUR_MULTION_API_KEY", local=False)

Browser = Agent(
    role="浏览器代理",
    goal="使用自然语言控制网络浏览器",
    backstory="一个专业的浏览代理。",
    tools=[multion_remote_tool],
    verbose=True,
)

# 用于搜索和总结新闻的示例任务
browse = Task(
    description="总结排名前 3 的热门 AI 新闻标题",
    expected_output="排名前 3 的热门 AI 新闻标题的摘要",
    agent=Browser,
)

crew = Crew(agents=[Browser], tasks=[browse])

crew.kickoff()
```

## 参数

- `api_key`：指定 MultiOn API 密钥。默认值为 `MULTION_API_KEY` 环境变量。
- `local`：使用设置为“true”的本地标志在您的浏览器上本地运行代理。确保已安装 multion 浏览器扩展程序并选中了“启用 API”。
- `max_steps`：可选。设置 multion 代理可以为命令执行的最大步骤数

## 入门步骤

要有效使用 `MultiOnTool`，请按照以下步骤操作：

1. **安装 CrewAI**：确认您的 Python 环境中已安装 `crewai[tools]` 软件包。
2. **安装并使用 MultiOn**：按照 MultiOn 文档安装 MultiOn 浏览器扩展程序 (https://docs.multion.ai/learn/browser-extension)。
3. **启用 API 使用**：单击浏览器扩展程序文件夹中的 MultiOn 扩展程序（不是网页上悬停的 MultiOn 图标）以打开扩展程序配置。单击“启用 API”切换按钮以启用 API。 
