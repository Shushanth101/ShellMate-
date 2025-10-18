import os
import subprocess
from typing import Optional
from langchain_core.tools import tool
import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote_plus
from langchain.tools import BaseTool
import os
from typing import List, Tuple
import subprocess


@tool(description="Reads file at the given path and returns string content of that file.")
def read_file(path: str) -> Optional[str]:
    """
    Reads the content of a file safely.

    Args:
        path (str): Path to the file.

    Returns:
        str: File content if successful, else None.
    """
    if not os.path.isfile(path):
        return f"Error: File '{path}' does not exist."
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file '{path}': {str(e)}"



@tool(description="Takes path and content as input and writes the content to the particular path")
def write_file(path: str, content: str) -> str:
    """
    Writes content to a file. Creates file if it doesn't exist.

    Args:
        path (str): Path to the file.
        content (str): Content to write.

    Returns:
        str: Success or error message.
    """
    try:
        dir_path = os.path.dirname(path)
        if dir_path:  # Only make directories if there's a parent path
            os.makedirs(dir_path, exist_ok=True)
        
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        
        return f"Successfully wrote to '{path}'."
    
    except Exception as e:
        return f"Error writing to file '{path}': {str(e)}"



@tool(description="takes a command as input and Executes command and returns the results.")
def execute_command(command: str) -> str:
    """
    Executes a shell command and returns its output.

    Args:
        command (str): Command to execute.

    Returns:
        str: Combined stdout and stderr.
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=False  
        )
        output = result.stdout.strip()
        error = result.stderr.strip()
        if error:
            return f"Error:\n{error}\nOutput:\n{output}"
        return output
    except Exception as e:
        return f"Exception executing command '{command}': {str(e)}"
    



@tool(description="""Perform a lightweight "Google Search" using RSS feeds.
    Args:
        query (str): Search query.
        max_items (int): Max number of results to return (1-10).
    Returns:
        list[dict]: List of search results with title, link, and published date (if available).""")
def google_search(query: str, max_items: int = 5)->list:
    """
    Perform a lightweight "Google Search" using RSS feeds.

    Args:
        query (str): Search query.
        max_items (int): Max number of results to return (1-10).

    Returns:
        list[dict]: List of search results with title, link, and published date (if available).
    """
    try:
        n = int(max_items)
    except Exception:
        n = 5
    n = max(1, min(10, n))  

    rss_url = f"https://news.google.com/rss/search?q={quote_plus(query)}&hl=en-US&gl=US&ceid=US:en"

    try:
        r = requests.get(rss_url, timeout=10)
        r.raise_for_status()
        root = ET.fromstring(r.content)
        items = root.findall(".//item")
        results = []
        for it in items[:n]:
            title = (it.findtext("title") or "").strip()
            link = (it.findtext("link") or "").strip()
            pub = (it.findtext("{http://purl.org/dc/elements/1.1/}date") or
                   it.findtext("pubDate") or "").strip()
            results.append({"title": title, "link": link, "published": pub})
        return results
    except Exception as e:
        return [{"error": str(e)}]





class CustomPythonREPLTool(BaseTool):
    name:str = "python_repl"
    description:str = "Executes Python code with a time limit."

    def _run(self, code: str, time_out: int = None):
        # Set default timeout if not provided or invalid
        timeout_value = time_out if isinstance(time_out, int) and time_out > 0 else 30

        try:
            process = subprocess.run(
                ['python', '-c', code],
                capture_output=True,
                text=True,
                timeout=timeout_value
            )
            return process.stdout.strip()
        except subprocess.TimeoutExpired:
            return f"Execution timed out after {timeout_value} seconds."
        except Exception as e:
            return f"An error occurred: {e}"



@tool(description="""List all files and folders separately in the given path.

    :param path: directory path
    :return: tuple (files, folders)""")
def readdir_detailed(path: str = ".") -> Tuple[List[str], List[str]]:
    files: List[str] = []
    folders: List[str] = []
    try:
        for entry in os.listdir(path):
            full_path = os.path.join(path, entry)
            if os.path.isfile(full_path):
                files.append(entry)
            elif os.path.isdir(full_path):
                folders.append(entry)
        return files, folders
    except FileNotFoundError:
        print(f"Error: Path '{path}' does not exist.")
        return [], []
    except PermissionError:
        print(f"Error: Permission denied for '{path}'.")
        return [], []

if __name__ == "__main__":
    print("--- READ FILE ---")
    print(read_file("test.txt"))

    print("--- WRITE FILE ---")
    print(write_file("test.txt", "Hello world!"))

    print("--- EXECUTE COMMAND ---")
    print(execute_command("echo 'Hello from shell!'"))
