import threading
import time
from typing import Any, Dict, Iterator, List, Optional, Tuple, Union

from langchain.agents import AgentExecutor
from langchain.agents.agent import ExceptionTool
from langchain.callbacks.manager import CallbackManagerForChainRun
from langchain_core.agents import AgentAction, AgentFinish, AgentStep
from langchain_core.exceptions import OutputParserException
from langchain_core.tools import BaseTool
from langchain_core.utils.input import get_color_mapping
from pydantic import InstanceOf

from crewai.agents.agent_builder.base_agent_executor_mixin import CrewAgentExecutorMixin
from crewai.agents.tools_handler import ToolsHandler
from crewai.tools.tool_usage import ToolUsage, ToolUsageErrorException
from crewai.utilities import I18N
from crewai.utilities.constants import TRAINING_DATA_FILE
from crewai.utilities.training_handler import CrewTrainingHandler


class CrewAgentExecutor(AgentExecutor, CrewAgentExecutorMixin):
    _i18n: I18N = I18N()
    should_ask_for_human_input: bool = False
    llm: Any = None
    iterations: int = 0
    task: Any = None
    tools_description: str = ""
    tools_names: str = ""
    original_tools: List[Any] = []
    crew_agent: Any = None
    crew: Any = None
    function_calling_llm: Any = None
    request_within_rpm_limit: Any = None
    tools_handler: Optional[InstanceOf[ToolsHandler]] = None
    max_iterations: Optional[int] = 15
    have_forced_answer: bool = False
    force_answer_max_iterations: Optional[int] = None  # type: ignore # Incompatible types in assignment (expression has type "int | None", base class "CrewAgentExecutorMixin" defined the type as "int")
    step_callback: Optional[Any] = None
    system_template: Optional[str] = None
    prompt_template: Optional[str] = None
    response_template: Optional[str] = None

    def _call(
        self,
        inputs: Dict[str, str],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, Any]:
        """运行文本并获取代理响应。"""
        # 构造一个工具名称到工具的映射，以便于查找
        name_to_tool_map = {tool.name: tool for tool in self.tools}
        # 我们构造了一个从每个工具到颜色的映射，用于日志记录。
        color_mapping = get_color_mapping(
            [tool.name.casefold() for tool in self.tools],
            excluded_colors=["green", "red"],
        )
        intermediate_steps: List[Tuple[AgentAction, str]] = []
        # 允许根据任务设置进行人工输入
        if self.task.human_input:
            self.should_ask_for_human_input = True

        # 让我们开始跟踪迭代次数和经过的时间
        self.iterations = 0
        time_elapsed = 0.0
        start_time = time.time()

        # 我们现在进入代理循环（直到它返回一些东西）。
        while self._should_continue(self.iterations, time_elapsed):
            if not self.request_within_rpm_limit or self.request_within_rpm_limit():
                next_step_output = self._take_next_step(
                    name_to_tool_map,
                    color_mapping,
                    inputs,
                    intermediate_steps,
                    run_manager=run_manager,
                )

                if self.step_callback:
                    self.step_callback(next_step_output)

                if isinstance(next_step_output, AgentFinish):
                    # 创建长期记忆
                    create_long_term_memory = threading.Thread(
                        target=self._create_long_term_memory, args=(next_step_output,)
                    )
                    create_long_term_memory.start()

                    return self._return(
                        next_step_output, intermediate_steps, run_manager=run_manager
                    )

                intermediate_steps.extend(next_step_output)

                if len(next_step_output) == 1:
                    next_step_action = next_step_output[0]
                    # 查看工具是否应该直接返回
                    tool_return = self._get_tool_return(next_step_action)
                    if tool_return is not None:
                        return self._return(
                            tool_return, intermediate_steps, run_manager=run_manager
                        )

                self.iterations += 1
                time_elapsed = time.time() - start_time
        output = self.agent.return_stopped_response(
            self.early_stopping_method, intermediate_steps, **inputs
        )

        return self._return(output, intermediate_steps, run_manager=run_manager)

    def _iter_next_step(
        self,
        name_to_tool_map: Dict[str, BaseTool],
        color_mapping: Dict[str, str],
        inputs: Dict[str, str],
        intermediate_steps: List[Tuple[AgentAction, str]],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Iterator[Union[AgentFinish, AgentAction, AgentStep]]:
        """在思考-行动-观察循环中迈出一步。

        覆盖此方法以控制代理如何做出选择并采取行动。
        """
        try:
            if self._should_force_answer():
                error = self._i18n.errors("force_final_answer")
                output = AgentAction("_Exception", error, error)
                self.have_forced_answer = True
                yield AgentStep(action=output, observation=error)
                return

            intermediate_steps = self._prepare_intermediate_steps(intermediate_steps)

            # 调用 LLM 以查看要做什么。
            output = self.agent.plan(  # type: ignore #  Incompatible types in assignment (expression has type "AgentAction | AgentFinish | list[AgentAction]", variable has type "AgentAction")
                intermediate_steps,
                callbacks=run_manager.get_child() if run_manager else None,
                **inputs,
            )

        except OutputParserException as e:
            if isinstance(self.handle_parsing_errors, bool):
                raise_error = not self.handle_parsing_errors
            else:
                raise_error = False
            if raise_error:
                raise ValueError(
                    "发生输出解析错误。 "
                    "为了将此错误传递回代理并让其重试，"
                    "请将 `handle_parsing_errors=True` 传递给 AgentExecutor。 "
                    f"错误如下：{str(e)}"
                )
            str(e)
            if isinstance(self.handle_parsing_errors, bool):
                if e.send_to_llm:
                    observation = f"\n{str(e.observation)}"
                    str(e.llm_output)
                else:
                    observation = ""
            elif isinstance(self.handle_parsing_errors, str):
                observation = f"\n{self.handle_parsing_errors}"
            elif callable(self.handle_parsing_errors):
                observation = f"\n{self.handle_parsing_errors(e)}"
            else:
                raise ValueError("获取到意外类型的 `handle_parsing_errors`")
            output = AgentAction("_Exception", observation, "")

            if run_manager:
                run_manager.on_agent_action(output, color="green")

            tool_run_kwargs = self.agent.tool_run_logging_kwargs()
            observation = ExceptionTool().run(
                output.tool_input,
                verbose=False,
                color=None,
                callbacks=run_manager.get_child() if run_manager else None,
                **tool_run_kwargs,
            )

            if self._should_force_answer():
                error = self._i18n.errors("force_final_answer")
                output = AgentAction("_Exception", error, error)
                yield AgentStep(action=output, observation=error)
                return

            yield AgentStep(action=output, observation=observation)
            return

        # 如果选择的工具是完成工具，则结束并返回。
        if isinstance(output, AgentFinish):
            if self.should_ask_for_human_input:
                human_feedback = self._ask_human_input(output.return_values["output"])

                if self.crew and self.crew._train:
                    self._handle_crew_training_output(output, human_feedback)

                # 确保我们只询问一次，因此在下一次思考循环中禁用
                self.should_ask_for_human_input = False
                action = AgentAction(
                    tool="Human Input", tool_input=human_feedback, log=output.log
                )

                yield AgentStep(
                    action=action,
                    observation=self._i18n.slice("human_feedback").format(
                        human_feedback=human_feedback
                    ),
                )
                return

            else:
                if self.crew and self.crew._train:
                    self._handle_crew_training_output(output)

                yield output
                return

        self._create_short_term_memory(output)

        actions: List[AgentAction]
        actions = [output] if isinstance(output, AgentAction) else output
        yield from actions

        for agent_action in actions:
            if run_manager:
                run_manager.on_agent_action(agent_action, color="green")

            tool_usage = ToolUsage(
                tools_handler=self.tools_handler,  # type: ignore # Argument "tools_handler" to "ToolUsage" has incompatible type "ToolsHandler | None"; expected "ToolsHandler"
                tools=self.tools,  # type: ignore # Argument "tools" to "ToolUsage" has incompatible type "Sequence[BaseTool]"; expected "list[BaseTool]"
                original_tools=self.original_tools,
                tools_description=self.tools_description,
                tools_names=self.tools_names,
                function_calling_llm=self.function_calling_llm,
                task=self.task,
                agent=self.crew_agent,
                action=agent_action,
            )
            tool_calling = tool_usage.parse(agent_action.log)

            if isinstance(tool_calling, ToolUsageErrorException):
                observation = tool_calling.message
            else:
                if tool_calling.tool_name.casefold().strip() in [
                    name.casefold().strip() for name in name_to_tool_map
                ] or tool_calling.tool_name.casefold().replace("_", " ") in [
                    name.casefold().strip() for name in name_to_tool_map
                ]:
                    observation = tool_usage.use(tool_calling, agent_action.log)
                else:
                    observation = self._i18n.errors("wrong_tool_name").format(
                        tool=tool_calling.tool_name,
                        tools=", ".join([tool.name.casefold() for tool in self.tools]),
                    )
            yield AgentStep(action=agent_action, observation=observation)

    def _handle_crew_training_output(
        self, output: AgentFinish, human_feedback: str | None = None
    ) -> None:
        """处理训练数据的函数。"""
        agent_id = str(self.crew_agent.id)

        if (
            CrewTrainingHandler(TRAINING_DATA_FILE).load()
            and not self.should_ask_for_human_input
        ):
            training_data = CrewTrainingHandler(TRAINING_DATA_FILE).load()
            if training_data.get(agent_id):
                training_data[agent_id][self.crew._train_iteration][
                    "improved_output"
                ] = output.return_values["output"]
                CrewTrainingHandler(TRAINING_DATA_FILE).save(training_data)

        if self.should_ask_for_human_input and human_feedback is not None:
            training_data = {
                "initial_output": output.return_values["output"],
                "human_feedback": human_feedback,
                "agent": agent_id,
                "agent_role": self.crew_agent.role,
            }
            CrewTrainingHandler(TRAINING_DATA_FILE).append(
                self.crew._train_iteration, agent_id, training_data
            )
