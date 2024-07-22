class Printer:
    """
    用于打印彩色文本的类。
    """

    def print(self, content: str, color: str):
        """
        根据指定的颜色打印文本内容。

        Args:
            content: 要打印的文本内容。
            color: 文本颜色，可选值：
                "purple"：紫色
                "red"：红色
                "bold_green"：粗体绿色
                "bold_purple"：粗体紫色
                "bold_blue"：粗体蓝色
                "yellow"：黄色
                其他值将使用默认颜色打印。
        """
        if color == "purple":
            self._print_purple(content)
        elif color == "red":
            self._print_red(content)
        elif color == "bold_green":
            self._print_bold_green(content)
        elif color == "bold_purple":
            self._print_bold_purple(content)
        elif color == "bold_blue":
            self._print_bold_blue(content)
        elif color == "yellow":
            self._print_yellow(content)
        else:
            print(content)  # 使用默认颜色打印

    def _print_bold_purple(self, content):
        """
        打印粗体紫色文本。
        """
        print("\033[1m\033[95m {}\033[00m".format(content))

    def _print_bold_green(self, content):
        """
        打印粗体绿色文本。
        """
        print("\033[1m\033[92m {}\033[00m".format(content))

    def _print_purple(self, content):
        """
        打印紫色文本。
        """
        print("\033[95m {}\033[00m".format(content))

    def _print_red(self, content):
        """
        打印红色文本。
        """
        print("\033[91m {}\033[00m".format(content))

    def _print_bold_blue(self, content):
        """
        打印粗体蓝色文本。
        """
        print("\033[1m\033[94m {}\033[00m".format(content))

    def _print_yellow(self, content):
        """
        打印黄色文本。
        """
        print("\033[93m {}\033[00m".format(content))
