from crewai.utilities.file_handler import PickleHandler


class CrewTrainingHandler(PickleHandler):
    """
    用于处理 CrewAI 训练数据的类，继承自 PickleHandler。
    """

    def save_trained_data(self, agent_id: str, trained_data: dict) -> None:
        """
        保存指定 Agent 的训练数据。

        参数:
        - agent_id (str): Agent 的 ID。
        - trained_data (dict): 要保存的训练数据。
        """
        data = self.load()  # 加载已有的数据
        data[agent_id] = trained_data  # 更新指定 Agent 的数据
        self.save(data)  # 保存数据

    def append(self, train_iteration: int, agent_id: str, new_data) -> None:
        """
        将新数据追加到现有的 Pickle 文件中。

        参数:
        - train_iteration (int): 训练迭代次数。
        - agent_id (str): Agent 的 ID。
        - new_data (object): 要追加的新数据。
        """
        data = self.load()  # 加载已有的数据

        if agent_id in data:
            data[agent_id][train_iteration] = new_data  # 将新数据添加到对应 Agent 和迭代次数下
        else:
            data[agent_id] = {
                train_iteration: new_data
            }  # 如果 Agent 不存在，则创建新的字典

        self.save(data)  # 保存数据
