import re


class YamlParser:
    """
    YAML 解析器类，用于解析 YAML 文件。
    """

    def parse(file):
        """
        解析 YAML 文件。

        Args:
            file: 要解析的 YAML 文件对象。

        Returns:
            解析后的 YAML 内容。

        Raises:
            ValueError: 如果 YAML 文件中存在不支持的语法。
        """
        content = file.read()  # 读取文件内容
        # Replace single { and } with doubled ones, while leaving already doubled ones intact and the other special characters {# and {%
        modified_content = re.sub(r"(?<!\{){(?!\{)(?!\#)(?!\%)", "{{", content)
        modified_content = re.sub(
            r"(?<!\})(?<!\%)(?<!\#)\}(?!})", "}}", modified_content
        )

        # 检查 'context:' 后面是否没有 '['，如果有则抛出错误
        if re.search(r"context:(?!\s*\[)", modified_content):
            raise ValueError(
                "目前仅在创建任务时代码中支持上下文。请在任务配置中使用 'context' 键。"
            )

        return modified_content  # 返回解析后的 YAML 内容
