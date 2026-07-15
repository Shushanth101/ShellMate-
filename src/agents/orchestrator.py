from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.messages import SystemMessage,HumanMessage,AnyMessage,ToolMessage
import operator
from typing import Literal
from typing_extensions import TypedDict, Annotated
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.checkpoint.mongodb import MongoDBSaver
from pymongo import MongoClient
from langchain_core.tools import tool
from src.tools.tools import web_fetch,web_search,read_file,write_file,python_repl,run_command,get_command_status,send_command_input,terminate_command,wait
from src.prompts.systemprompts import ORCHESTRATOR_AGENT_SYSTEM_PROMPT
from dotenv import load_dotenv
import os

load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
mongo_client = MongoClient("mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.3.4")


llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
tools = [
    web_fetch,
    web_search,
    read_file,
    write_file,
    run_command,
    python_repl,
    get_command_status,
    send_command_input,
    terminate_command,
    wait
]
tools_by_name = {t.name: t for t in tools}
model_with_tools = llm.bind_tools(tools)


class MessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    llm_calls: int


def llm_call(state: dict):
    return {
        "messages": [
            model_with_tools.invoke(
                [SystemMessage(content=ORCHESTRATOR_AGENT_SYSTEM_PROMPT)] + state["messages"]
            )
        ],
        "llm_calls": state.get("llm_calls", 0) + 1
    }



def tool_node(state: dict):
    result = []
    for tool_call in state["messages"][-1].tool_calls:
        tool = tools_by_name[tool_call["name"]]

        if tool_call["name"] == "retrieve_image_content":
            b64_images = tool.invoke(tool_call["args"])
            result.append(ToolMessage("Here are the retrieved images", tool_call_id=tool_call["id"]))
            for img in b64_images:
                result.append(HumanMessage(content=[
                    {"type": "text", "text": "Retrieved image"},
                    {"type": "image_url", "image_url": {"url": f"data:{img['mime_type']};base64,{img['data']}"}}
                ]))
        else:
            observation = tool.invoke(tool_call["args"])
            result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))

    return {"messages": result}

def should_continue(state: MessagesState) -> Literal["tool_node", "__end__"]:
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tool_node"
    return "__end__"


checkpointer = MongoDBSaver(mongo_client)

agent_builder = StateGraph(MessagesState)
agent_builder.add_node("llm_call", llm_call)
agent_builder.add_node("tool_node", tool_node)
agent_builder.add_edge(START, "llm_call")
agent_builder.add_conditional_edges("llm_call", should_continue, ["tool_node", "__end__"])
agent_builder.add_edge("tool_node", "llm_call")

agent = agent_builder.compile(checkpointer=checkpointer)