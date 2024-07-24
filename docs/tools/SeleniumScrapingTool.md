# SeleniumScrapingTool 文档

!!! note "实验性"
    我们仍在努力改进工具，因此未来可能会更改本文档。
    :octicons-mark-github-16: [SeleniumScrapingTool 源代码](https://github.com/aithoughts/aipmAI-tools/tree/zh/src/crewai_tools/tools/selenium_scraping_tool)

## 描述
SeleniumScrapingTool 专为高效的网页抓取任务而设计。它允许通过使用 CSS 选择器来定位特定元素，从而从网页中精确提取内容。其设计满足了广泛的抓取需求，提供了处理任何提供的网站 URL 的灵活性。

## 安装
要开始使用 SeleniumScrapingTool，请使用 pip 安装 crewai_tools 包：

```
pip install 'crewai[tools]'
```

## 使用示例
以下是一些可以使用 SeleniumScrapingTool 的场景：

```python
from crewai_tools import SeleniumScrapingTool

# 示例 1：初始化工具，无需任何参数即可抓取其导航到的当前页面
tool = SeleniumScrapingTool()

# 示例 2：抓取给定 URL 的整个网页
tool = SeleniumScrapingTool(website_url='https://example.com')

# 示例 3：从网页中定位并抓取特定的 CSS 元素
tool = SeleniumScrapingTool(website_url='https://example.com', css_element='.main-content')

# 示例 4：使用其他参数执行抓取以获得自定义体验
tool = SeleniumScrapingTool(website_url='https://example.com', css_element='.main-content', cookie={'name': 'user', 'value': 'John Doe'}, wait_time=10)
```

## 参数
以下参数可用于自定义 SeleniumScrapingTool 的抓取过程：

- `website_url`：**必填**。指定要从中抓取内容的网站的 URL。
- `css_element`：**必填**。要定位在网站上的特定元素的 CSS 选择器。这使得能够集中抓取网页的特定部分。
- `cookie`：**可选**。包含 cookie 信息的字典。用于模拟登录会话，从而提供对可能仅限于未登录用户的内容的访问权限。
- `wait_time`：**可选**。指定抓取内容之前的延迟（以秒为单位）。此延迟允许网站和任何动态内容完全加载，从而确保成功抓取。

!!! attention
    由于 SeleniumScrapingTool 处于积极开发中，因此参数和功能可能会随着时间的推移而发展。鼓励用户保持工具更新并报告任何问题或增强建议。
