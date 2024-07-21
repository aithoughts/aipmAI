import subprocess
import click


def replay_task_command(task_id: str) -> None:
    """
    从特定任务重放 crew 执行。

    参数：
      task_id (str)：要重放的任务的 ID。
    """
    command = ["poetry", "run", "replay", task_id]  # 构造要执行的命令

    try:
        result = subprocess.run(command, capture_output=False, text=True, check=True)  # 执行命令
        if result.stderr:  # 如果命令执行过程中出现错误
            click.echo(result.stderr, err=True)  # 输出错误信息

    except subprocess.CalledProcessError as e:  # 如果命令执行失败
        click.echo(f"重放任务时出错: {e}", err=True)  # 输出错误信息
        click.echo(e.output, err=True)  # 输出命令执行的输出

    except Exception as e:  # 如果出现其他异常
        click.echo(f"发生意外错误: {e}", err=True)  # 输出错误信息
