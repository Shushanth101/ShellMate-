from langchain_core.tools import tool
import requests
from langchain.tools import BaseTool
import os
from typing import List, Tuple
import subprocess
from pathlib import Path
from typing import Dict,List, Optional
from InquirerPy import inquirer
from rich.panel import Panel
from rich.console import Console
from utils.utilityfunctions  import typewriter_effect
import subprocess
from dotenv import load_dotenv
from utils.utilityfunctions import generate_rich_diff


load_dotenv()

console = Console()
BASE_DIR = Path(__file__).resolve().parent
MEMORY_FILE = os.path.join(BASE_DIR,"memory.txt")


# --- Logging Helpers ---
# Keeping these simple but they look good in the console

def log_info(msg: str):
    console.print(f"\n [bold cyan][🟦 ShellMate][/bold cyan] ",end="")
    console.print(msg)
    print()

def log_success(msg: str):
    console.print(f"[bold green][🟩 Success][/bold green] ",end="")
    console.print(msg)
    print()

def log_error(msg: str):
    console.print(f"[bold red][🟥 Error][/bold red] ",end="")
    console.print(msg)
    print()

def log_command(msg: str):
    console.print(f"[bold yellow][🟧 Command][/bold yellow] ",end="")
    console.print(msg)
    print()

def log_warning(msg: str):
    console.print(f"[bold yellow][🟨 Warning][/bold yellow] ",end="")
    console.print(msg)
    print()



@tool(description="Reads file at the given path and returns string content of that file.")
def read_file(path: str) -> Optional[str]:
    """Cracking open a file to see what's inside."""
    log_info(f"Peeking into: 📖 [white]{path}[/white]")

    if not os.path.isfile(path):
        log_error(f"Can't see it. File's missing: {path}")
        return f"Error: File '{path}' does not exist."
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        log_success(f"📖 Got the contents of: {path}")
        return content

    except Exception as e:
        log_error(f"Failed to read {path}. Reason: {e}")
        return f"Error reading file '{path}': {str(e)}"

@tool(description="Takes path and content as input and writes the content to that path.")
def write_file(path: str, content: str) -> str:
    """Scribbling some notes into a file."""
    log_info(f"📝 Writing to:  [white]{path}[/white]")

    try:
        dir_path = os.path.dirname(path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
            log_info(f"📂 Making sure the folder exists: [white]{dir_path}[/white]")
        
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        log_success(f"📝 Saved to: {path}")
        return f"Successfully wrote to '{path}'."

    except Exception as e:
        log_error(f"Couldn't write to {path}. Reason: {e}")
        return f"Error writing to file '{path}': {str(e)}"

@tool(description= "Takes path and new content as input, shows diff and asks user to accept or reject changes.")
def edit_file(path: str, new_content: str) -> str:
    """Time for some edits. Asking the boss for approval first."""
    old_content = ""
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            old_content = f.read()

    diff_text = generate_rich_diff(old_content, new_content, path)
    print()

    console.print(
        Panel(
            diff_text,
            title=f"[bold cyan]Proposed Changes → {path}[/bold cyan]",
            border_style="bright_blue",
            padding=(1, 2),
        )
    )
    
    prompt = inquirer.select(
        message="What do you think?",
        choices=["Accept", "Reject"],
    ).execute()
    
    choice = prompt

    if choice == "Accept":
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)
        console.print(f"[bold green]✓ Done. Updated {path}[/bold green]")
        return "applied changes."

    else:
        console.print(f"[bold red]✗ Alright, discarding changes.[/bold red]")
        return "user rejected changes." 
     
    

@tool(description="Use LangSearch Web Search API to search internet web pages. The input should be a search query string, and the output will return detailed information of search results, including web page title, web page URL, web page content, web page publication time, etc.")
def web_search(query: str, summary:bool, count: int = 5) -> str:
    """Scouring the web for answers."""
    LANGSEARCH_API_KEY = os.getenv("LANGSEARCH_API_KEY")
    url = "https://api.langsearch.com/v1/web-search"
    headers = {
        "Authorization": f"Bearer {LANGSEARCH_API_KEY}",  
        "Content-Type": "application/json"
    }
    data = {
        "query": query,
        "freshness": "noLimit",  
        "summary": summary,
        "count": count
    }
    log_info(f"🌐 Googling (well, searching) for: [white]{query}[/white]")
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        json_response = response.json()
        try:
            if json_response["code"] != 200 or not json_response["data"]:
                return f"Search failed, reason: {response.msg or 'Unknown error'}"
            
            webpages = json_response["data"]["webPages"]["value"]
            if not webpages:
                return "Came up empty."
            formatted_results = ""
            for idx, page in enumerate(webpages, start=1):
                formatted_results += (
                    f"Citation: {idx}\n"
                    f"Title: {page['name']}\n"
                    f"URL: {page['url']}\n"
                    f"Content: {page['summary']}\n"
                )
            return formatted_results.strip()
        except Exception as e:
            return f"Search broke parsing results: {str(e)}"
    else:
        return f"Search API error: {response.status_code}, {response.text}"


class CustomPythonREPLTool(BaseTool):
    name: str = "python_repl"
    description: str = "Executes Python code with a time limit."

    def _run(self, code: str, time_out: int = None):
        log_info("Running some Python code...")
        console.print(Panel(code,title="[bold cyan]The Logic[/bold cyan]",border_style="bright_blue",padding=(1,2)))

        timeout_value = time_out if isinstance(time_out, int) and time_out > 0 else 30

        # Human in the loop
        action = inquirer.select(
            message="Run this?",
            choices=["Yes", "No"]
        ).execute()

        if action == "No":
            log_warning("❌ Aborted by user.")
            return "Operation Cancelled by user."

        try:
            process = subprocess.run(
                ['python', '-c', code],
                capture_output=True,
                text=True,
                timeout=timeout_value
            )

            stdout = process.stdout.strip()
            stderr = process.stderr.strip()

            if stderr:
                log_error("Python crashed.")
                console.print(Panel(stderr, title="[red]stderr[/red]", style="red"))

            if stdout:
                log_success("Python returned:")
                console.print(Panel(stdout, title="[green]stdout[/green]", style="green"))

            return stdout

        except subprocess.TimeoutExpired:
            log_error(f"Code took too long (>{timeout_value}s).")
            return f"Execution timed out after {timeout_value} seconds."
        except Exception as e:
            log_error(f"Python error: {e}")
            return f"An error occurred: {e}"


@tool(description="Lists files and folders separately in the given path.")
def readdir_detailed(path: str = ".") -> Tuple[List[str], List[str]]:
    """Scanning the directory."""
    log_info(f"📂 Checking out: {path}")

    files = []
    folders = []

    try:
        for entry in os.listdir(path):
            full = os.path.join(path, entry)
            if os.path.isfile(full):
                files.append(entry)
            elif os.path.isdir(full):
                folders.append(entry)

        log_success("📂 Done listing files.")
        return files, folders

    except FileNotFoundError:
        log_error(f"📂 Can't find that path: {path}")
        return [], []
    except PermissionError:
        log_error(f"📂 Don't have permission for: {path}")
        return [], []

@tool(description="Use this tool for asking the questions to user..its just a beautiful wrapper...")
def prompt_user(message:str,options:List[str])-> str:
    """Asking the user a question."""
    response = inquirer.select(
        message=message,
        choices=options
    ).execute()
    return response

import database as db

SHELL_STATE = {"cwd": os.getcwd()}

@tool(description="Executes shell command. Use interactive=True to open external terminal.")
def execute_command(command: str, interactive: bool = False):
    """
    Running a command in the terminal.
    
    - interactive=True → Pop open a new window.
    - interactive=False → Run it here.
    """

    # Human in the loop
    action = inquirer.select(
        message=f"Run command: {command}?",
        choices=["Yes", "No"]
    ).execute()

    if action == "No":
        log_warning("❌ User said no.")
        return "Command execution cancelled by user."

    log_info(f"Firing off: {command}")
    log_command(command)

    if interactive:
        log_info("🚀 Opening a new window for this...")

        try:
            subprocess.Popen(
                ["cmd.exe", "/k", command],
                cwd=SHELL_STATE["cwd"],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )

            log_success("🚀 Terminal launched.")

            return "Opened a new terminal for you."

        except Exception as e:
            log_error(f"🚀 Couldn't pop the terminal: {e}")
            return f"Error: {e}"

   
    else:
        log_info("Running quietly inside ShellMate...")
        
        try:
            result = subprocess.run(
                command,
                cwd=SHELL_STATE["cwd"], 
                shell=True,
                capture_output=True,
                text=True,
                check=False
            )

            stdout = result.stdout.strip()
            stderr = result.stderr.strip()

            if stderr:
                log_error("🚀 Command complained.")
                console.print(Panel(stderr, title="[red]stderr[/red]", style="red"))

                if stdout:
                    console.print(Panel(stdout, title="[yellow]stdout[/yellow]", style="yellow"))

                return f"Error:\n{stderr}\nOutput:\n{stdout} (CWD: {SHELL_STATE['cwd']})"

            log_success("🚀 Command finished successfully.")
            if stdout:
                console.print(Panel(stdout, title="[green]stdout[/green]", style="green"))

            return (stdout if stdout else "Command executed.") + f"\n(Current Directory: {SHELL_STATE['cwd']})"

        except Exception as e:
            log_error(f"🚀 Crashed running command: {e}")
            return f"Exception executing '{command}': {e}"

@tool(
    description=(
        "Display a formatted list of TODO items to the user."
    )
)
def write_todos(todos: List[str]) -> str:
    """Making a nice checklist for the user."""
    if not todos:
        console.print("[yellow]Empty list? Nothing to do![/yellow]")
        return "No todos to display."
    
    cleaned_todos = [todo.strip() for todo in todos if todo.strip()]
    
    if not cleaned_todos:
        console.print("[yellow]Nothing valid in that list.[/yellow]")
        return "No valid todos to display."
    
    formatted_todos = [f"☐ {i+1}. {todo}" for i, todo in enumerate(cleaned_todos)]
    todos_string = "\n".join(formatted_todos)
    
    todo_count = len(cleaned_todos)
    title = f"[cyan]TODO's ({todo_count} item{'s' if todo_count != 1 else ''})[/cyan]"
    
    console.print(Panel(
        todos_string,
        title=title,
        style="yellow",
        border_style="cyan"
    ))
    
    return f"Showed {todo_count} todos to the user."
