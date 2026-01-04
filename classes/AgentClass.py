import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from langchain.agents import create_agent
import uuid
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.tools import tool
from utils.tools import read_file,write_file,readdir_detailed,web_search,CustomPythonREPLTool,execute_command,prompt_user,edit_file,write_todos
from utils.system_prompt import get_system_prompt
from api_client import client
from langchain.messages import HumanMessage,AIMessage
from rich.console import Console

console = Console()

class Agent:
    def __init__(self, model, history=None, user_id=None):
        self.model = model
        self.user_id = user_id
        self.history = history
        self.thread_id = uuid.uuid4()
        self.config:RunnableConfig={"configurable":{"thread_id":self.thread_id}}
        self.checkpointer = InMemorySaver()
        # Keep a local copy of the conversation
        self.internal_messages = [] if history is None else list(history)

        user_facts = ""
        if self.user_id:
            # Let's see what we know about this person
            user_facts = client.get_facts()
            
        system_prompt = get_system_prompt(user_facts)

        @tool(description="Appends a user-related fact or piece of information to the ShellMate memory.")
        def store_user_facts_tool(fact: str) -> str:
            """Jotting this down in my notebook."""
            if not self.user_id:
                return "Can't remember things for anonymous users."

            console.print(f"[bold green][🟩 Memory Updated][/bold green]")
            res = client.store_fact(fact)
            if res.get("success"):
                return "Got it. Memory saved."
            return "Oops, couldn't write that down."
        
        # Equip the agent
        python_repl = CustomPythonREPLTool()
        self.tools = [read_file, write_file, execute_command, python_repl, web_search, readdir_detailed, prompt_user, edit_file, store_user_facts_tool,write_todos]

        # Birth of the agent
        self.agent = create_agent(model=self.model, checkpointer=self.checkpointer, tools=self.tools, system_prompt=system_prompt)
        
        if self.history:
            # Load up the past context
            self.agent.update_state(
                self.config,
                {"messages": self.history}
            )
            # Make sure we're in sync
            if not self.internal_messages and self.history:
                self.internal_messages = list(self.history)
            

    def invoke(self,query):
        # One-shot interaction
        response = self.agent.invoke({"messages":[{"role":"user","content":query}]},config=self.config)
        
        # Log it
        self.internal_messages.append(HumanMessage(content=query))
        self.internal_messages.append(AIMessage(content=response["messages"][-1].content))
        
        return response["messages"][-1].content
    
    def stream(self, query):
        # Flowing interaction
        full_response = ""
        for token,metadata in self.agent.stream(
            {"messages": [{"role":"user","content":query}]},
            stream_mode="messages",
            config=self.config
        ):
            if metadata["langgraph_node"] == "model":
                for block in token.content_blocks:
                    if block["type"] == "text" and block["text"]:
                        full_response += block["text"]
                        yield {"content": block["text"]}
                
                    if block["type"] == "tool_call_chunk":
                        yield {"tool_call":block["name"]}
                        
        
        # Log the full exchange
        self.internal_messages.append(HumanMessage(content=query))
        self.internal_messages.append(AIMessage(content=full_response))
    
    def get_messages(self):
        # Hand over the transcript
        return self.internal_messages