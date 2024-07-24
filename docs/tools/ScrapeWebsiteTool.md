# ScrapeWebsiteTool 文档

!!! note "实验性"
    我们仍在努力改进工具，因此未来可能会更改本文档。
    :octicons-mark-github-16: [ScrapeWebsiteTool 源代码](https://github.com/aithoughts/aipmAI-tools/tree/zh/src/crewai_tools/tools/scrape_website_tool)

## 描述
此工具旨在提取和读取指定网站的内容。它能够通过发出 HTTP 请求和解析接收到的 HTML 内容来处理各种类型的网页。此工具对于网页抓取任务、数据收集或从网站提取特定信息特别有用。

## 安装
安装 crewai_tools 包
```shell
pip install 'crewai[tools]'
```

## 示例
```python
from crewai_tools import ScrapeWebsiteTool

# 启用抓取其执行期间找到的任何网站
tool = ScrapeWebsiteTool()

# 使用网站 URL 初始化工具，以便代理只能抓取指定网站的内容
tool = ScrapeWebsiteTool(website_url='https://example.com')

# 从网站提取文本
text = tool.run()
print(text)
```

## 参数
- `website_url` ：要读取文件的强制性网站 URL。这是该工具的主要输入，指定应抓取和读取哪个网站的内容。
