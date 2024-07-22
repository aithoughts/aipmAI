import os
import pickle


from datetime import datetime


class FileHandler:
    """负责文件操作，目前仅将消息记录到文件中。"""

    def __init__(self, file_path):
        """
        初始化 FileHandler 对象。

        参数：
        - file_path (bool 或 str): 文件路径。如果为 True，则使用默认路径 "logs.txt"；如果为字符串，则使用指定路径。
        """
        if isinstance(file_path, bool):
            self._path = os.path.join(os.curdir, "logs.txt")  # 使用默认路径
        elif isinstance(file_path, str):
            self._path = file_path  # 使用指定路径
        else:
            raise ValueError("file_path 必须是布尔值或字符串。")

    def log(self, **kwargs):
        """
        将消息记录到文件中。

        参数：
        - **kwargs: 要记录的消息，以键值对形式传递。
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 获取当前时间
        message = f"{now}: ".join([f"{key}={value}" for key, value in kwargs.items()])  # 格式化消息
        with open(self._path, "a", encoding="utf-8") as file:  # 以追加模式打开文件
            file.write(message + "\n")  # 将消息写入文件


class PickleHandler:
    """负责使用 pickle 序列化和反序列化数据到文件。"""

    def __init__(self, file_name: str) -> None:
        """
        初始化 PickleHandler 对象。

        参数：
        - file_name (str): 用于保存和加载数据的文件名。文件将保存在当前目录中。
        """
        self.file_path = os.path.join(os.getcwd(), file_name)  # 获取文件路径

    def initialize_file(self) -> None:
        """
        如果文件不存在或为空，则用空字典初始化文件。
        """
        if not os.path.exists(self.file_path) or os.path.getsize(self.file_path) == 0:
            self.save({})  # 保存空字典以初始化文件

    def save(self, data) -> None:
        """
        使用 pickle 将数据保存到指定文件。

        参数：
        - data (object): 要保存的数据。
        """
        with open(self.file_path, "wb") as file:  # 以二进制写入模式打开文件
            pickle.dump(data, file)  # 使用 pickle 将数据保存到文件

    def load(self) -> dict:
        """
        使用 pickle 从指定文件加载数据。

        返回：
        - dict: 从文件中加载的数据。
        """
        if not os.path.exists(self.file_path) or os.path.getsize(self.file_path) == 0:
            return {}  # 如果文件不存在或为空，则返回空字典

        with open(self.file_path, "rb") as file:  # 以二进制读取模式打开文件
            try:
                return pickle.load(file)  # 使用 pickle 从文件加载数据
            except EOFError:
                return {}  # 如果文件为空或损坏，则返回空字典
            except Exception:
                raise  # 抛出加载过程中发生的任何其他异常
