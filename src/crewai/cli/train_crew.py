import subprocess

import click


def train_crew(n_iterations: int) -> None:
    """
    通过在 Poetry 环境中运行命令来训练 crew。

    参数：
        n_iterations (int)：训练 crew 的迭代次数。
    """
    command = ["poetry", "run", "train", str(n_iterations)]  # 构造要执行的命令

    try:
        if n_iterations <= 0:  # 如果迭代次数小于等于 0
            raise ValueError("迭代次数必须为正整数。")  # 抛出异常

        result = subprocess.run(command, capture_output=False, text=True, check=True)  # 执行命令

        if result.stderr:  # 如果命令执行过程中出现错误
            click.echo(result.stderr, err=True)  # 输出错误信息

    except subprocess.CalledProcessError as e:  # 如果命令执行失败
        click.echo(f"训练 crew 时出错: {e}", err=True)  # 输出错误信息
        click.echo(e.output, err=True)  # 输出命令执行的输出

    except Exception as e:  # 如果出现其他异常
        click.echo(f"发生意外错误: {e}", err=True)  # 输出错误信息
