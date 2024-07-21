from langchain.tools import StructuredTool

from crewai.agents.agent_builder.utilities.base_agent_tool import BaseAgentTools


class AgentTools(BaseAgentTools):
    """默认的代理委托工具"""

    def tools(self):
        coworkers = ", ".join([f"{agent.role}" for agent in self.agents])
        tools = [
            StructuredTool.from_function(
                func=self.delegate_work,
                name="委托工作给同事",
                description=self.i18n.tools("delegate_work").format(
                    coworkers=coworkers
                ),
            ),
            StructuredTool.from_function(
                func=self.ask_question,
                name="向同事提问",
                description=self.i18n.tools("ask_question").format(coworkers=coworkers),
            ),
        ]
        return tools
