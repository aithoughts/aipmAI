import os
from pathlib import Path

import click


def create_crew(name):
    """创建一个新的 crew。"""
    folder_name = name.replace(" ", "_").replace("-", "_").lower()  # 将名称转换为文件夹名
    class_name = name.replace("_", " ").replace("-", " ").title().replace(" ", "")  # 将名称转换为类名

    click.secho(f"正在创建文件夹 {folder_name}...", fg="green", bold=True)  # 输出信息，表示正在创建文件夹

    if not os.path.exists(folder_name):  # 如果文件夹不存在
        os.mkdir(folder_name)  # 创建文件夹
        os.mkdir(folder_name + "/tests")  # 创建 tests 文件夹
        os.mkdir(folder_name + "/src")  # 创建 src 文件夹
        os.mkdir(folder_name + f"/src/{folder_name}")  # 创建 src/{folder_name} 文件夹
        os.mkdir(folder_name + f"/src/{folder_name}/tools")  # 创建 tools 文件夹
        os.mkdir(folder_name + f"/src/{folder_name}/config")  # 创建 config 文件夹
        with open(folder_name + "/.env", "w") as file:  # 创建 .env 文件
            file.write("OPENAI_API_KEY=YOUR_API_KEY")  # 写入 API 密钥
    else:
        click.secho(  # 输出信息，表示文件夹已存在
            f"\t文件夹 {folder_name} 已存在。请选择其他名称。",
            fg="red",
        )
        return

    package_dir = Path(__file__).parent  # 获取当前文件所在目录的父目录
    templates_dir = package_dir / "templates"  # 获取 templates 目录

    # 要复制的模板文件列表
    root_template_files = [
        ".gitignore",
        "pyproject.toml",
        "README.md",
    ]
    tools_template_files = ["tools/custom_tool.py", "tools/__init__.py"]
    config_template_files = ["config/agents.yaml", "config/tasks.yaml"]
    src_template_files = ["__init__.py", "main.py", "crew.py"]

    # 复制根目录下的模板文件
    for file_name in root_template_files:
        src_file = templates_dir / file_name
        dst_file = Path(folder_name) / file_name
        copy_template(src_file, dst_file, name, class_name, folder_name)

    # 复制 src 目录下的模板文件
    for file_name in src_template_files:
        src_file = templates_dir / file_name
        dst_file = Path(folder_name) / "src" / folder_name / file_name
        copy_template(src_file, dst_file, name, class_name, folder_name)

    # 复制 tools 目录下的模板文件
    for file_name in tools_template_files:
        src_file = templates_dir / file_name
        dst_file = Path(folder_name) / "src" / folder_name / file_name
        copy_template(src_file, dst_file, name, class_name, folder_name)

    # 复制 config 目录下的模板文件
    for file_name in config_template_files:
        src_file = templates_dir / file_name
        dst_file = Path(folder_name) / "src" / folder_name / file_name
        copy_template(src_file, dst_file, name, class_name, folder_name)

    click.secho(f"Crew {name} 创建成功！", fg="green", bold=True)  # 输出信息，表示 crew 创建成功


def copy_template(src, dst, name, class_name, folder_name):
    """将文件从 src 复制到 dst。"""
    with open(src, "r") as file:
        content = file.read()  # 读取文件内容

    # 替换文件内容中的占位符
    content = content.replace("{{name}}", name)
    content = content.replace("{{crew_name}}", class_name)
    content = content.replace("{{folder_name}}", folder_name)

    # 将替换后的内容写入新文件
    with open(dst, "w") as file:
        file.write(content)

    click.secho(f"  - 已创建 {dst}", fg="green")  # 输出信息，表示已创建文件
