---
title: 使用 AgentOps 进行代理监控
description: 使用 AgentOps 了解和记录您的代理性能。
---

# 简介
可观察性是开发和部署对话式 AI 代理的一个关键方面。它允许开发人员了解其代理的执行情况、代理与用户的交互方式以及代理如何使用外部工具和 API。AgentOps 是一款独立于 CrewAI 的产品，为代理提供了全面的可观察性解决方案。

## AgentOps

[AgentOps](https://agentops.ai/?=aipm) 为代理提供会话回放、指标和监控。

在较高的层次上，AgentOps 使您能够监控成本、令牌使用情况、延迟、代理故障、会话范围的统计数据等。有关更多信息，请查看 [AgentOps 仓库](https://github.com/AgentOps-AI/agentops)。

### 概述
AgentOps 提供对开发和生产环境中代理的监控。它提供了一个用于跟踪代理性能、会话回放和自定义报告的仪表板。

此外，AgentOps 还提供会话钻取功能，用于实时查看 Crew 代理交互、LLM 调用和工具使用情况。此功能对于调试和了解代理如何与用户以及其他代理交互非常有用。

![一系列选定代理会话运行的概述](..%2Fassets%2Fagentops-overview.png)
![用于检查代理运行的会话钻取的概述](..%2Fassets%2Fagentops-session.png)
![查看逐步代理回放执行图](..%2Fassets%2Fagentops-replay.png)

### 特性
- **LLM 成本管理和跟踪**：跟踪与基础模型提供商的支出。
- **回放分析**：观看逐步代理执行图。
- **递归思维检测**：识别代理何时陷入无限循环。
- **自定义报告**：创建有关代理性能的自定义分析。
- **分析仪表板**：监控有关开发和生产环境中代理的高级统计信息。
- **公共模型测试**：根据基准和排行榜测试您的代理。
- **自定义测试**：针对特定领域的测试运行您的代理。
- **时间旅行调试**：从检查点重新启动您的会话。
- **合规性和安全性**：创建审计日志并检测潜在威胁，例如亵渎和 PII 泄露。
- **提示注入检测**：识别潜在的代码注入和秘密泄露。

### 使用 AgentOps

1. **创建 API 密钥：**
   在此处创建用户 API 密钥：[创建 API 密钥](https://app.agentops.ai/account)

2. **配置您的环境：**
   将您的 API 密钥添加到您的环境变量中

   ```bash
   AGENTOPS_API_KEY=<您的 AGENTOPS API 密钥>
   ```

3. **安装 AgentOps：**
   使用以下命令安装 AgentOps：
   ```bash
   pip install crewai[agentops]
   ```
   或
   ```bash
   pip install agentops
   ```

   在您的脚本中使用 `Crew` 之前，请包含以下行：

   ```python
   import agentops
   agentops.init()
   ```

   这将启动 AgentOps 会话并自动跟踪 Crew 代理。有关如何配置更复杂的代理系统的更多信息，请查看 [AgentOps 文档](https://docs.agentops.ai) 或加入 [Discord](https://discord.gg/j4f3KbeH)。

### Crew + AgentOps 示例
- [职位发布](https://github.com/aithoughts/aipmAI-examples/tree/main/job-posting)
- [Markdown 验证器](https://github.com/aithoughts/aipmAI-examples/tree/main/markdown_validator)
- [Instagram 帖子](https://github.com/aithoughts/aipmAI-examples/tree/main/instagram_post)

### 更多信息

要开始使用，请创建一个 [AgentOps 帐户](https://agentops.ai/?=aipm)。

有关功能请求或错误报告，请在 [AgentOps 仓库](https://github.com/AgentOps-AI/agentops) 上联系 AgentOps 团队。

#### 其他链接

<a href="https://twitter.com/agentopsai/">🐦 Twitter</a>
<span>&nbsp;&nbsp;•&nbsp;&nbsp;</span>
<a href="https://discord.gg/JHPt4C7r">📢 Discord</a>
<span>&nbsp;&nbsp;•&nbsp;&nbsp;</span>
<a href="https://app.agentops.ai/?=aipm">🖇️ AgentOps 仪表板</a>
<span>&nbsp;&nbsp;•&nbsp;&nbsp;</span>
<a href="https://docs.agentops.ai/introduction">📙 文档</a>
