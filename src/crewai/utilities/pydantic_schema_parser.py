from typing import Type, get_args, get_origin

from pydantic import BaseModel


class PydanticSchemaParser(BaseModel):
    """
    用于解析 Pydantic 模型并生成其 Schema 的类。
    """

    model: Type[BaseModel]  # 要解析的 Pydantic 模型类

    def get_schema(self) -> str:
        """
        获取 Pydantic 模型的 Schema。

        :return: 模型 Schema 的字符串表示。
        """
        return self._get_model_schema(self.model)

    def _get_model_schema(self, model, depth=0) -> str:
        """
        递归获取模型的 Schema。

        :param model: 要获取 Schema 的模型。
        :param depth: 当前递归深度。
        :return: 模型 Schema 的字符串表示。
        """
        lines = []
        for field_name, field in model.model_fields.items():  # 遍历模型字段
            field_type_str = self._get_field_type(
                field, depth + 1
            )  # 获取字段类型字符串
            lines.append(
                f"{' ' * 4 * depth}- {field_name}: {field_type_str}"
            )  # 添加字段信息到列表

        return "\n".join(lines)  # 将列表转换为字符串并返回

    def _get_field_type(self, field, depth) -> str:
        """
        获取字段类型的字符串表示。

        :param field: 要获取类型的字段。
        :param depth: 当前递归深度。
        :return: 字段类型的字符串表示。
        """
        field_type = field.annotation  # 获取字段类型注解
        if get_origin(field_type) is list:  # 如果是列表类型
            list_item_type = get_args(field_type)[
                0
            ]  # 获取列表元素类型
            if isinstance(list_item_type, type) and issubclass(
                list_item_type, BaseModel
            ):  # 如果是嵌套的 Pydantic 模型
                nested_schema = self._get_model_schema(
                    list_item_type, depth + 1
                )  # 递归获取嵌套模型的 Schema
                return f"List[\n{nested_schema}\n{' ' * 4 * depth}]"
            else:  # 否则直接返回列表元素类型名称
                return f"List[{list_item_type.__name__}]"
        elif issubclass(field_type, BaseModel):  # 如果是 Pydantic 模型
            return f"\n{self._get_model_schema(field_type, depth)}"  # 递归获取模型 Schema
        else:  # 否则直接返回类型名称
            return field_type.__name__
