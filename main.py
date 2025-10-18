from rich.console import Console
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn
import uuid
from gemini import executor
from dblogging import log_conversation

console = Console()

SESSION_ID = str(uuid.uuid4())

def main():
    console.print("[bold cyan]Welcome to ShellMate CLI![/bold cyan]")
    console.print("[dim]Type 'exit' or 'bye' to quit.[/dim]\n")

    while True:
        query = Prompt.ask("[bold green]You[/bold green]")
        if query.lower() in ["exit", "bye"]:
            console.print("\n[bold magenta]Goodbye![/bold magenta]")
            break

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            task = progress.add_task("ShellMate is thinking...", start=False)
            progress.start_task(task)
            
            
            result = executor.invoke({"input": query})

        
        tools_used = []
        for step in result.get("intermediate_steps", []):
            action, _ = step
            tools_used.append(action.tool)
        tools_used = list(set(tools_used)) 
        
        
        log_conversation(
            session_id=SESSION_ID,
            user_input=query,
            agent_output=result["output"],
            tools_used=tools_used
        )

        console.print("\n[bold yellow]ShellMate:[/bold yellow]")
        console.print(result["output"], style="white on black")
        console.print("==" * 50)  
    




if __name__ == "__main__":
    main()
