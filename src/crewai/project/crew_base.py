import inspect
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv
from pydantic import ConfigDict

load_dotenv()


def CrewBase(cls):
    """
    一个装饰器，用于标记一个类为 Crew 的基类。
    它会加载代理和任务的配置，并将它们存储在 self.agents_config 和 self.tasks_config 中。
    """
    class WrappedClass(cls):
        model_config = ConfigDict(arbitrary_types_allowed=True)
        is_crew_class: bool = True  # type: ignore

        base_directory = None
        for frame_info in inspect.stack():
            if "site-packages" not in frame_info.filename:
                base_directory = Path(frame_info.filename).parent.resolve()
                break

        if base_directory is None:
            raise Exception(
                "无法动态确定项目的根目录，您必须从项目的根目录运行它。"
            )

        original_agents_config_path = getattr(
            cls, "agents_config", "config/agents.yaml"
        )
        original_tasks_config_path = getattr(cls, "tasks_config", "config/tasks.yaml")

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.agents_config = self.load_yaml(
                os.path.join(self.base_directory, self.original_agents_config_path)
            )
            self.tasks_config = self.load_yaml(
                os.path.join(self.base_directory, self.original_tasks_config_path)
            )

        @staticmethod
        def load_yaml(config_path: str):
            """
            从给定的路径加载 YAML 配置文件。
            """
            with open(config_path, "r") as file:
                # parsedContent = YamlParser.parse(file)  # type: ignore # 传递给“parse”的参数 1 的类型“TextIOWrapper”与“YamlParser”不兼容
                return yaml.safe_load(file)

    return WrappedClass
