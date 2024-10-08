import yaml
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor
from langchain_core.messages import HumanMessage, AIMessage
from langchain.agents.format_scratchpad import format_to_tool_messages
from langchain.agents.output_parsers import ToolsAgentOutputParser

# custom tools and prompt
from .tools import insert_data, search_data, update_data, delete_data
from .prompt import custom_prompt


# loading the config file and environment variables
load_dotenv()
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)


class DatabaseAgent:
    def __init__(self):
        self.__tools = [insert_data, search_data, update_data, delete_data]
        self.__llm_with_tool = ChatGroq(model=config["agent-model-name"]).bind_tools(tools=self.__tools)
        self.__agent = (
            {
                "input": lambda x: x["input"],
                "chat_history": lambda x: x["chat_history"],
                "agent_scratchpad": lambda x: format_to_tool_messages(x["intermediate_steps"])
            }
            | custom_prompt
            | self.__llm_with_tool
            | ToolsAgentOutputParser()
        )
        self.__agent_executor = AgentExecutor(agent=self.__agent, tools=self.__tools, verbose=True)
        self.__chat_history = []
    
    
    def get_response(self, query):
        response = self.__agent_executor.invoke(input={"input": query, "chat_history": self.__chat_history})
        # appending user query and agent response to the chat history
        self.__chat_history.extend(
            [
                HumanMessage(content=query),
                AIMessage(content=response["output"])
            ]
        )
        return response["output"]

