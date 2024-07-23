import click
import pkg_resources

from crewai.memory.storage.kickoff_task_outputs_storage import (
    KickoffTaskOutputsSQLiteStorage,
)


from .create_crew import create_crew
from .train_crew import train_crew
from .replay_from_task import replay_task_command
from .reset_memories_command import reset_memories_command


@click.group()
def crewai():
    """crewai 的顶级命令组。"""


@crewai.command()
@click.argument("project_name")
def create(project_name):
    """创建一个新的 crew。"""
    create_crew(project_name)


@crewai.command()
@click.option(
    "--tools", is_flag=True, help="显示已安装的 crewai 工具版本"
)
def version(tools):
    """显示已安装的 crewai 版本。"""
    crewai_version = pkg_resources.get_distribution("crewai").version
    click.echo(f"crewai 版本: {crewai_version}")

    if tools:
        try:
            tools_version = pkg_resources.get_distribution("aipmai-tools").version
            click.echo(f"crewai 工具版本: {tools_version}")
        except pkg_resources.DistributionNotFound:
            click.echo("crewai 工具未安装")


@crewai.command()
@click.option(
    "-n",
    "--n_iterations",
    type=int,
    default=5,
    help="训练 crew 的迭代次数",
)
def train(n_iterations: int):
    """训练 crew。"""
    click.echo(f"正在训练 crew {n_iterations} 次迭代")
    train_crew(n_iterations)


@crewai.command()
@click.option(
    "-t",
    "--task_id",
    type=str,
    help="从此任务 ID（包括所有后续任务）重放 crew。",
)
def replay(task_id: str) -> None:
    """
    从特定任务重放 crew 执行。

    参数：
        task_id (str)：要重放的任务的 ID。
    """
    try:
        click.echo(f"正在从任务 {task_id} 重放 crew")
        replay_task_command(task_id)
    except Exception as e:
        click.echo(f"重放时出错: {e}", err=True)


@crewai.command()
def log_tasks_outputs() -> None:
    """
    检索您最新的 crew.kickoff() 任务输出。
    """
    try:
        storage = KickoffTaskOutputsSQLiteStorage()
        tasks = storage.load()

        if not tasks:
            click.echo(
                "未找到任务输出。仅记录 crew kickoff 任务输出。"
            )
            return

        for index, task in enumerate(tasks, 1):
            click.echo(f"任务 {index}: {task['task_id']}")
            click.echo(f"描述: {task['expected_output']}")
            click.echo("------")

    except Exception as e:
        click.echo(f"记录任务输出时出错: {e}", err=True)


@crewai.command()
@click.option("-l", "--long", is_flag=True, help="重置长期记忆")
@click.option("-s", "--short", is_flag=True, help="重置短期记忆")
@click.option("-e", "--entities", is_flag=True, help="重置实体记忆")
@click.option(
    "-k",
    "--kickoff-outputs",
    is_flag=True,
    help="重置最新的 KICKOFF 任务输出",
)
@click.option("-a", "--all", is_flag=True, help="重置所有记忆")
def reset_memories(long, short, entities, kickoff_outputs, all):
    """
    重置 crew 记忆（长期、短期、实体、最新的 crew_kickoff_ouputs）。这将删除所有已保存的数据。
    """
    try:
        if not all and not (long or short or entities or kickoff_outputs):
            click.echo(
                "请使用适当的标志指定至少一种要重置的记忆类型。"
            )
            return
        reset_memories_command(long, short, entities, kickoff_outputs, all)
    except Exception as e:
        click.echo(f"重置记忆时出错: {e}", err=True)


if __name__ == "__main__":
    crewai()
