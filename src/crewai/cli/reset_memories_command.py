import subprocess
import click

from crewai.memory.entity.entity_memory import EntityMemory
from crewai.memory.long_term.long_term_memory import LongTermMemory
from crewai.memory.short_term.short_term_memory import ShortTermMemory
from crewai.utilities.task_output_storage_handler import TaskOutputStorageHandler


def reset_memories_command(long, short, entity, kickoff_outputs, all) -> None:
    """
    重置 crew 记忆。

    参数：
      long (bool)：是否重置长期记忆。
      short (bool)：是否重置短期记忆。
      entity (bool)：是否重置实体记忆。
      kickoff_outputs (bool)：是否重置最新的 kickoff 任务输出。
      all (bool)：是否重置所有记忆。
    """

    try:
        if all:  # 如果重置所有记忆
            ShortTermMemory().reset()  # 重置短期记忆
            EntityMemory().reset()  # 重置实体记忆
            LongTermMemory().reset()  # 重置长期记忆
            TaskOutputStorageHandler().reset()  # 重置最新的 kickoff 任务输出
            click.echo("所有记忆已重置。")  # 输出信息，表示所有记忆已重置
        else:  # 否则，根据参数分别重置记忆
            if long:
                LongTermMemory().reset()
                click.echo("长期记忆已重置。")

            if short:
                ShortTermMemory().reset()
                click.echo("短期记忆已重置。")
            if entity:
                EntityMemory().reset()
                click.echo("实体记忆已重置。")
            if kickoff_outputs:
                TaskOutputStorageHandler().reset()
                click.echo("已存储的最新 Kickoff 输出已重置。")

    except subprocess.CalledProcessError as e:  # 如果命令执行失败
        click.echo(f"重置记忆时出错: {e}", err=True)  # 输出错误信息
        click.echo(e.output, err=True)  # 输出命令执行的输出

    except Exception as e:  # 如果出现其他异常
        click.echo(f"发生意外错误: {e}", err=True)  # 输出错误信息
    