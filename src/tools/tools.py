from typing import Optional
import time
from dotenv import load_dotenv
from langchain_core.tools import tool
import requests
import os
import sys
import json
from langchain.tools import BaseTool
import subprocess
from src.tools.shell_tool import ShellTool


load_dotenv()

OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")

@tool("web_search")
def web_search(
    query: str,
    max_results: int = 5,
    timeout: int = 10,
) -> list[dict]:
    """
    Search the web using Ollama Web Search API.

    Args:
        query: Search query.
        max_results: Number of results to return (1-10).
        timeout: Request timeout in seconds.

    Returns:
        List of search results.
        Each result contains:
        {
            "title": str,
            "url": str,
            "content": str
        }
    """

    response = requests.post(
        "https://ollama.com/api/web_search",
        headers={"Authorization":f"Bearer {OLLAMA_API_KEY}"},
        json={
            "query": query,
            "max_results": min(max_results, 10)
        },
        timeout=timeout
    )

    response.raise_for_status()

    return response.json().get("results", [])    
    
@tool("web_fetch")
def web_fetch(
    url: str,
    timeout: int = 10,
) -> dict:
    """
    Fetch a web page using Ollama's Web Fetch API.

    Args:
        url: URL of the page to fetch.
        timeout: Request timeout in seconds.

    Returns:
        {
            "title": str,
            "content": str,
            "links": list[str]
        }
    """

    response = requests.post(
        "https://ollama.com/api/web_fetch",
        headers={"Authorization":f"Bearer {OLLAMA_API_KEY}"},
        json={"url": url},
        timeout=timeout
    )

    response.raise_for_status()

    data = response.json()

    return {
        "title": data.get("title", ""),
        "content": data.get("content", ""),
        "links": data.get("links", [])
    }


@tool("read_file",description="Reads file at the given path and returns string content of that file.")
def read_file(path: str) -> Optional[str]:
    """Cracking open a file to see what's inside."""

    if not os.path.isfile(path):
        return f"Error: File '{path}' does not exist."
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        return content

    except Exception as e:
        return f"Error reading file '{path}': {str(e)}"

@tool("write_file",description="Takes path and content as input and writes the content to that path.")
def write_file(path: str, content: str) -> str:
    """Scribbling some notes into a file."""
    try:
        dir_path = os.path.dirname(path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        return f"Successfully wrote to '{path}'."

    except Exception as e:
        return f"Error writing to file '{path}': {str(e)}"
    

shell_tool = ShellTool()

@tool(
    description="Executes a command in a persistent shell. Returns a commandId which you must use with get_command_status to see the output."
)
def run_command(command_line: str, cwd: str = os.getcwd()) -> dict:
    """
    Executes a command in a persistent PTY session.
    Best for interactive or long-running commands.
    """

    result = shell_tool.run_command(command_line, cwd=cwd)

    return result




@tool(
    description="Checks the status and gets the most recent output of a command started with run_command."
)
def get_command_status(command_id: str, char_limit: int = 1000) -> dict:
    """
    Checks the status and returns the latest output.
    """

    result = shell_tool.get_command_status(
        command_id,
        char_limit=char_limit
    )

    return result


@tool(
    description="Sends text/input to a running interactive command."
)
def send_command_input(command_id: str, input_text: str) -> dict:
    """
    Sends input to an interactive process.
    """

    return shell_tool.send_command_input(
        command_id,
        input_text
    )


@tool(
    description="Force terminates a running command."
)
def terminate_command(command_id: str) -> dict:
    """
    Terminates a running PTY session.
    """

    return shell_tool.terminate_command(command_id)


@tool(
    description="Waits for a specified number of seconds. Use this to pause execution while long-running processes are working."
)
def wait(seconds: int) -> str:
    """
    Pause execution.
    """

    time.sleep(seconds)
    return f"Waited for {seconds} seconds."


class CustomPythonREPLTool(BaseTool):
    name: str = "python_repl"
    description: str = "Executes Python code with a time limit."

    def _run(self, code: str, time_out: int = 30) -> str:
        """
        Execute Python code in a subprocess with a timeout.
        """

        timeout_value = (
            time_out
            if isinstance(time_out, int) and time_out > 0
            else 30
        )

        try:
            process = subprocess.run(
                ["python", "-c", code],
                capture_output=True,
                text=True,
                timeout=timeout_value
            )

            stdout = process.stdout.strip()
            stderr = process.stderr.strip()

            if stderr:
                return f"Error:\n{stderr}"

            return stdout if stdout else "Code executed successfully."

        except subprocess.TimeoutExpired:
            return f"Execution timed out after {timeout_value} seconds."

        except Exception as e:
            return f"An error occurred: {e}"

python_repl = CustomPythonREPLTool()
