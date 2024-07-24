# DirectoryReadTool 文档

!!! note "实验性"
    我们仍在努力改进工具，因此未来可能会更改本文档。
    :octicons-mark-github-16: [DirectoryReadTool 源代码](https://github.com/aithoughts/aipmAI-tools/tree/zh/src/crewai_tools/tools/directory_read_tool)

## 描述
DirectoryReadTool 是一款功能强大的实用程序，旨在提供目录内容的全面列表。它可以递归地浏览指定的目录，为用户提供所有文件的详细枚举，包括子目录中的文件。此工具对于需要全面清点目录结构或验证目录中文件组织的任务至关重要。

## 安装
要在您的项目中使用 DirectoryReadTool，请安装 `crewai_tools` 包。如果您的环境中还没有此软件包，则可以使用 pip 使用以下命令安装它：

```shell
pip install 'crewai[tools]'
```

此命令将安装最新版本的 `crewai_tools` 包，从而可以访问 DirectoryReadTool 以及其他实用程序。

## 示例
使用 DirectoryReadTool 非常简单。以下代码片段演示了如何设置它并使用该工具列出指定目录的内容：

```python
from crewai_tools import DirectoryReadTool

# 初始化工具，以便代理可以读取其在执行期间了解到的任何目录的内容
tool = DirectoryReadTool()

# 或

# 使用特定目录初始化工具，以便代理只能读取指定目录的内容
tool = DirectoryReadTool(directory='/path/to/your/directory')
```

## 参数
DirectoryReadTool 需要最少的配置才能使用。此工具的基本参数如下：

- `directory`: **可选**。指定要列出其内容的目录的路径的参数。它接受绝对路径和相对路径，引导工具前往所需的目录以列出内容。
