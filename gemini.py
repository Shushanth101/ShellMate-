from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate,MessagesPlaceholder
from system_prompt import system_prompt
from langchain.memory import ConversationBufferMemory
from langchain.agents import create_tool_calling_agent,AgentExecutor
from tools import read_file,write_file,execute_command,google_search,CustomPythonREPLTool
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


dotenv_path = BASE_DIR / ".env"
load_dotenv(dotenv_path)


os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")
model_id = os.getenv("MODEL_ID")

llm = ChatGoogleGenerativeAI(
    model=model_id,
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

memory = ConversationBufferMemory(return_messages=True,memory_key="chat_history",output_key="output")


prompt = ChatPromptTemplate.from_messages([
    ("system",system_prompt),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human","{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])

python_repl = CustomPythonREPLTool()

tools = [read_file,write_file,execute_command,google_search,python_repl]


agent = create_tool_calling_agent(llm=llm,prompt=prompt,tools=tools)

executor = AgentExecutor(agent=agent,tools=tools,memory=memory)



