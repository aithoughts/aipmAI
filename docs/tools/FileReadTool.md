# FileReadTool 文档

!!! note "实验性"
    我们仍在努力改进工具，因此未来可能会更改本文档。
    :octicons-mark-github-16: [FileReadTool 源代码](https://github.com/aithoughts/aipmAI-tools/tree/zh/src/crewai_tools/tools/file_read_tool)

## 描述
FileReadTool 概念上代表了 crewai_tools 包中的一套功能，旨在促进文件读取和内容检索。该套件包括用于处理批处理文本文件、读取运行时配置文件和导入数据以进行分析的工具。它支持各种基于文本的文件格式，例如 `.txt`、`.csv`、`.json` 等。根据文件类型，该套件提供专门的功能，例如将 JSON 内容转换为 Python 字典以便于使用。

## 安装
要使用以前归属于 FileReadTool 的功能，请安装 crewai_tools 包：

```shell
pip install 'crewai[tools]'
```

## 使用示例
FileReadTool 入门：

```python
from crewai_tools import FileReadTool

# 初始化工具以读取代理知道或学习路径的任何文件
file_read_tool = FileReadTool()

# 或

# 使用特定的文件路径初始化工具，以便代理只能读取指定文件的内容
file_read_tool = FileReadTool(file_path='path/to/your/file.txt')
```

## 参数
- `file_path`：要读取的文件的路径。它接受绝对路径和相对路径。确保文件存在并且您具有访问该文件的必要权限。
