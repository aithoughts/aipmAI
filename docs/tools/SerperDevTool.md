# SerperDevTool 文档

!!! note "实验性"
    我们仍在努力改进工具，因此未来可能会更改本文档。
    :octicons-mark-github-16: [SerperDevTool 源代码](https://github.com/aithoughts/aipmAI-tools/tree/zh/src/crewai_tools/tools/serper_dev_tool)

## 描述
此工具旨在根据用户提供的查询，在互联网上对文本内容执行语义搜索。它利用 [serper.dev](https://serper.dev) API 获取并显示基于用户提供查询的最相关搜索结果。

## 安装
要将此工具集成到您的项目中，请按照以下安装说明进行操作：
```shell
pip install 'crewai[tools]'
```

## 示例
以下示例演示了如何初始化工具并使用给定查询执行搜索：

```python
from crewai_tools import SerperDevTool

# 初始化该工具以实现互联网搜索功能
tool = SerperDevTool()
```

## 入门步骤
要有效地使用 `SerperDevTool`，请按照以下步骤操作：

1. **软件包安装**: 确认您的 Python 环境中已安装 `crewai[tools]` 软件包。
2. **API 密钥获取**: 通过在 `serper.dev` 上注册免费帐户来获取 `serper.dev` API 密钥。
3. **环境配置**: 将您获得的 API 密钥存储在名为 `SERPER_API_KEY` 的环境变量中，以便该工具使用。

## 总结
通过将 `SerperDevTool` 集成到 Python 项目中，用户可以直接从其应用程序执行实时、相关的互联网搜索。通过遵循提供的设置和使用指南，将此工具集成到项目中变得简便易行。
