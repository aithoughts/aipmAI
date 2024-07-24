# SpiderTool 文档

!!! note "实验性"
    我们仍在努力改进工具，因此未来可能会更改本文档。
    :octicons-mark-github-16: [SpiderTool 源代码](https://github.com/aithoughts/aipmAI-tools/tree/zh/src/crewai_tools/tools/spider_tool)

## 描述

[Spider](https://spider.cloud/?ref=crewai) 是[最快](https://github.com/spider-rs/spider/blob/main/benches/BENCHMARKS.md#benchmark-results)的开源抓取器和爬虫，它返回 LLM 就绪的数据。它将任何网站转换为纯 HTML、Markdown、元数据或文本，同时使您能够使用 AI 进行自定义操作的爬取。

## 安装

要使用 Spider API，您需要下载 [Spider SDK](https://pypi.org/project/spider-client/) 和 crewai[tools] SDK：

```python
pip install spider-client 'crewai[tools]'
```

## 示例

此示例向您展示如何使用 Spider 工具使您的代理能够抓取和爬取网站。Spider API 返回的数据已经是 LLM 就绪的，因此无需进行任何清理。

```python
from crewai_tools import SpiderTool

def main():
    spider_tool = SpiderTool()
    
    searcher = Agent(
        role="网络研究专家",
        goal="从特定 URL 查找相关信息",
        backstory="一位非常擅长使用网络的网络研究专家",
        tools=[spider_tool],
        verbose=True,
    )

    return_metadata = Task(
        description="抓取 https://spider.cloud，限制为 1 并启用元数据",
        expected_output="spider.cloud 的元数据和 10 个字的摘要",
        agent=searcher
    )

    crew = Crew(
        agents=[searcher],
        tasks=[
            return_metadata, 
        ],
        verbose=2
    )
    
    crew.kickoff()

if __name__ == "__main__":
    main()
```

## 参数

- `api_key`（字符串，可选）：指定 Spider API 密钥。如果未指定，它会在环境变量中查找 `SPIDER_API_KEY`。
- `params`（对象，可选）：请求的可选参数。默认为 `{"return_format": "markdown"}`，以返回更适合 LLM 的格式的网站内容。
    - `request`（字符串）：要执行的请求类型。可能的值为 `http`、`chrome` 和 `smart`。使用 `smart` 默认执行 HTTP 请求，直到 HTML 需要 JavaScript 渲染。
    - `limit`（整数）：每个网站允许爬取的最大页面数。删除该值或将其设置为 `0` 以爬取所有页面。
    - `depth`（整数）：最大深度的爬取限制。如果为 `0`，则不应用限制。
    - `cache`（布尔值）：对爬取使用 HTTP 缓存以加快重复运行速度。默认为 `true`。
    - `budget`（对象）：具有路径和计数器的对象，用于限制页面数量，例如 `{"*":1}` 仅爬取根页面。
    - `locale`（字符串）：用于请求的语言环境，例如 `en-US`。
    - `cookies`（字符串）：添加用于请求的 HTTP cookie。
    - `stealth`（布尔值）：对无头 chrome 请求使用隐身模式以帮助防止被阻止。chrome 上的默认值为 `true`。
    - `headers`（对象）：转发用于所有请求的 HTTP 标头。该对象应为键值对的映射。
    - `metadata`（布尔值）：布尔值，用于存储有关找到的页面和内容的元数据。这可能有助于提高 AI 互操作性。默认为 `false`，除非您已存储启用了配置的网站。
    - `viewport`（对象）：配置 chrome 的视口。默认为 `800x600`。
    - `encoding`（字符串）：要使用的编码类型，例如 `UTF-8`、`SHIFT_JIS` 等。
    - `subdomains`（布尔值）：允许包含子域。默认为 `false`。
    - `user_agent`（字符串）：向请求添加自定义 HTTP 用户代理。默认情况下，这设置为随机代理。
    - `store_data`（布尔值）：布尔值，用于确定是否应使用存储。如果设置，则优先于 `storageless`。默认为 `false`。
    - `gpt_config`（对象）：使用 AI 生成在爬取期间执行的操作。您可以为 `"prompt"` 传递一个数组来链接步骤。
    - `fingerprint`（布尔值）：对 chrome 使用高级指纹。
    - `storageless`（布尔值）：布尔值，用于防止存储请求的任何类型的数据，包括存储和 AI 向量嵌入。默认为 `false`，除非您已经存储了网站。
    - `readability`（布尔值）：使用 [readability](https://github.com/mozilla/readability) 对内容进行预处理以供阅读。这可能会极大地改善 LLM 使用的内容。
    `return_format`（字符串）：返回数据的格式。可能的值为 `markdown`、`raw`、`text` 和 `html2text`。使用 `raw` 返回页面的默认格式，例如 HTML 等。
    - `proxy_enabled`（布尔值）：为请求启用高性能高级代理，以防止在网络级别被阻止。
    - `query_selector`（字符串）：从标记中提取内容时使用的 CSS 查询选择器。
    - `full_resources`（布尔值）：爬取并下载网站的所有资源。
    - `request_timeout`（整数）：用于请求的超时时间。超时时间可以是 `5-60`。默认值为 `30` 秒。
    - `run_in_background`（布尔值）：在后台运行请求。如果存储数据并希望触发对仪表板的爬取，则此选项很有用。如果设置了 storageless，则此选项无效。
