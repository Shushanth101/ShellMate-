from utils.utilityfunctions import gradient_banner, multiline_prompt
from termcolor import colored
from InquirerPy import inquirer
from constants import welcome_messages, models
import random
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from classes.AgentClass import Agent
from rich.console import Console
from rich.panel import Panel
# Removed rich.markdown, rich.live, rich.spinner as requested
import argparse
import sys
import getpass
import subprocess
import time
from api_client import client

# Initialization stuff
load_dotenv()
console = Console()

def start_server():
    """Starts the Flask server in a subprocess."""
    console.print("[dim]Startup: Spinning up the ShellMate server...[/dim]")
    
    # We gotta make sure we find the server script no matter where we run from
    base_dir = os.path.dirname(os.path.abspath(__file__))
    server_script = os.path.join(base_dir, "server.py")
    
    # Fire it up silently
    server_process = subprocess.Popen([sys.executable, server_script], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Give it a sec to breathe and connect
    retries = 10
    while retries > 0:
        if client.check_health():
            console.print("[dim]Connected to the backend. We're good to go.[/dim]")
            return server_process
        time.sleep(1)
        retries -= 1
    
    # If we're here, something went wrong
    console.print("[bold red]Could not talk to the server. Shimmying out.[/bold red]")
    server_process.kill()
    sys.exit(1)

def get_credentials(args, confirm_password=False):
    """Grab the username and password from the user."""
    username = args.username
    if not username:
        username = input("Who goes there? (Username): ").strip()
    
    password = args.password
    if not password:
        password = getpass.getpass("Secrets please (Password): ").strip()
        
    # If we're signing up, better double check that password
    if confirm_password and not args.password: 
        confirm = getpass.getpass("Say it again (Confirm Password): ").strip()
        while password != confirm:
            console.print("[red]Those didn't match. Let's try that again.[/red]")
            password = getpass.getpass("Password: ").strip()
            confirm = getpass.getpass("Confirm Password: ").strip()
            
    return username, password

def start_session(agent, messages_log, user_id):
    """Kick off the main chat loop."""
    
    # Clean slate
    os.system('cls' if os.name == 'nt' else 'clear')
    print(gradient_banner("> S H E L L"))
    print(gradient_banner("  M A T E"))
    
    # If we have history, show it off
    if messages_log:
        console.print(Panel("[dim]Picking up where we left off...[/dim]", style="dim"))
        for msg in messages_log:
            # Determining who said what
            msg_type = msg.get("type", None)
            role = msg.get("role", None)

            # Map to our UI roles
            if msg_type == "human" or role == "user":
                ui_role = "user"
            elif msg_type == "ai" or role == "assistant":
                ui_role = "assistant"
            else:
                # Ignore system noise
                continue

            content = msg.get("content", "")
            
            # Skip empty AI messages (often internal tool calls)
            if ui_role == "assistant" and not content:
                continue
                
            role_color = "magenta" if ui_role == "assistant" else "cyan"
            # Simple, human-readable prefixes
            prefix = "Shelly: " if ui_role == "assistant" else "You: "
            
            print(colored(prefix, color=role_color, attrs=['bold']), end="")
            print(colored(content, color="white", attrs=['bold']), end="\n\n")
    else:
        # Fresh start
        welcome_message = random.choice(welcome_messages)
        print(colored(welcome_message,color="cyan",attrs=['bold']))
        print("\n",colored("(Hit Ctrl+T to send your thoughts — Enter just adds a new line)",color="white",attrs=['bold']))
        print(colored("Protip: /save <title> to keep this chat, /exit to bail", color="yellow"))
        console.print(f"[dim]Current spot: {os.getcwd()}[/dim]")
        print()

    # The conversation loop
    while True:
        try:
            user_text = multiline_prompt()
            print()
        except KeyboardInterrupt:
            console.print(Panel("[bold yellow]Catch you later![/bold yellow]", border_style="yellow", padding=(1, 2)))
            break
            
        cmd = user_text.strip().lower()
        if cmd in ["exit", "quit", "/exit"]:
            console.print(Panel("[bold yellow]Catch you later![/bold yellow]", border_style="yellow", padding=(1, 2)))
            break
        
        # Saving the good times
        if cmd.startswith("/save"):
            if not user_id:
                console.print("[bold red]Can't save ghost chats. Login first![/bold red]")
                continue
            
            parts = user_text.strip().split(' ', 1)
            if len(parts) < 2:
                console.print("[bold red]Gimme a title! Usage: /save <title>[/bold red]")
                continue
                
            title = parts[1].strip()
            console.print(f"[bold cyan]Saving this as '{title}'...[/bold cyan]")
            
            # Pack it up for the API
            raw_messages = agent.get_messages()
            serialized_messages = []
            for msg in raw_messages:
                serialized_messages.append(msg.dict())

            res = client.save_chat(serialized_messages, title)
            if res.get("success"):
                console.print(f"[bold green]✓ {res.get('message')}[/bold green]")
            else:
                 console.print(f"[bold red]✗ Save failed: {res.get('message')}[/bold red]")
            continue
            
        try:
            print("==" * 20)
            
            # Here comes the response... raw and unfiltered
            # print("Shelly: ", end="", flush=True) # Optional prompt before streaming?
            # Actually, standard flow usually prints role first.
            print(colored("Shelly: ", "magenta", attrs=['bold']), end="", flush=True)

            stream = agent.stream(user_text)
            
            full_response = ""
            for event in stream:
                # Just print the text as it arrives. No spinners. No markdown parsing.
                if event.get("content"):
                    chunk = event["content"]
                    print(chunk, end="", flush=True)
                    full_response += chunk
            
            print() # Newline at the end
            print()

        except Exception as e:
            console.print(f"[bold red]Oof, brain freeze: {e}[/bold red]")


def main():
    parser = argparse.ArgumentParser(description="ShellMate - Your AI CLI Buddy")
    
    # The keys to the castle
    parser.add_argument("--signup", action="store_true", help="Join the crew")
    parser.add_argument("--login", action="store_true", help="Welcome back")
    parser.add_argument("--anonymous", action="store_true", help="Go incognito (No history saved)")
    parser.add_argument("--username", type=str, help="Your handle")
    parser.add_argument("--password", type=str, help="The secret word")
    
    # Extra goodies
    parser.add_argument("--chats", action="store_true", help="Check your archives")
    parser.add_argument("--model", type=str, help="Pick your brain") 

    # Boot up the backend first
    server_process = start_server()
    
    try:
        args = parser.parse_args()

        user_id = None
        current_model = None

        # --- Getting In ---
        if args.anonymous:
            # Stay unknown
            pass 
        
        elif args.signup:
            console.print("[bold cyan]Let's get you signed up[/bold cyan]")
            u, p = get_credentials(args, confirm_password=True)
            res = client.signup(u, p)
            if res.get("success"):
                console.print(f"[bold green]✓ {res.get('message')}[/bold green]")
                # Smooth entry after signup
                login_res = client.login(u, p)
                if login_res.get("success"):
                     user_id = login_res.get("user_id")
                else:
                     console.print("Weird, login failed right after signup.")
                     sys.exit(1)
            else:
                console.print(f"[bold red]✗ {res.get('message')}[/bold red]")
                sys.exit(1)

        elif args.login or args.chats: 
            if not (args.username and args.password):
                 console.print("[bold cyan]Login time[/bold cyan]")
            
            u, p = get_credentials(args)
            login_res = client.login(u, p)
            
            if login_res.get("success"):
                user_id = login_res.get("user_id")
                current_model = login_res.get("model")
            else:
                console.print(f"[bold red]✗ {login_res.get('message')}[/bold red]")
                sys.exit(1)

        else:
            # Menu time
            print(gradient_banner("> S H E L L"))
            print(gradient_banner("  M A T E"))
            
            choice = inquirer.select(
                message="Yo! What's the plan?",
                choices=["Login", "Signup", "Continue as Anonymous", "Exit"]
            ).execute()

            if choice == "Login":
                u = input("Username: ")
                p = getpass.getpass("Password: ")
                login_res = client.login(u, p)
                if login_res.get("success"):
                    user_id = login_res.get("user_id")
                    current_model = login_res.get("model")
                else:
                    console.print(f"[bold red]✗ {login_res.get('message')}[/bold red]")
                    server_process.kill()
                    sys.exit(1)

            elif choice == "Signup":
                u = input("New Username: ")
                p = getpass.getpass("New Password: ")
                c = getpass.getpass("Confirm Password: ")
                if p != c:
                     console.print("[bold red]Those passwords clashed.[/bold red]")
                     server_process.kill()
                     sys.exit(1)
                     
                res = client.signup(u, p)
                if res.get("success"):
                    console.print(f"[bold green]✓ {res.get('message')}[/bold green]")
                    login_res = client.login(u, p)
                    user_id = login_res.get("user_id")
                else:
                    console.print(f"[bold red]✗ {res.get('message')}[/bold red]")
                    server_process.kill()
                    sys.exit(1)
            
            elif choice == "Exit":
                server_process.kill()
                sys.exit(0)

        # --- Chat History Check ---
        start_history = []
        
        if user_id and not args.chats: 
             # We're in, give options
             sub_choice = inquirer.select(
                message="What's next?",
                choices=["New Chat", "Resume Chat"]
            ).execute()
             
             if sub_choice == "Resume Chat":
                 args.chats = True 

        if args.chats:
            if not user_id:
                console.print("[bold red]Need to be logged in for that.[/bold red]")
                server_process.kill()
                sys.exit(1)
            
            chats = client.get_chats()
            if not chats:
                console.print("[yellow]No history found. Fresh start![/yellow]")
            else:
                # Pick a winner
                options = [f"[{c['id']}] {c['date']} - {c['title']}" for c in chats]
                options.append("Back to New Chat")
                
                selected = inquirer.select(
                    message="Pick a conversation:",
                    choices=options
                ).execute()
                
                if selected != "Back to New Chat":
                    chat_id = int(selected.split(']')[0].strip('['))
                    start_history = client.get_chat_content(chat_id)
                    if not start_history:
                         console.print("[red]Couldn't grab that chat.[/red]")
                         server_process.kill()
                         sys.exit(1)

        # --- The Brains ---
        if args.model:
            selected_model = args.model
        elif current_model:
             selected_model = inquirer.select(
                message="Which brain do you want today?",
                choices=models,
                default=current_model
            ).execute()
        else:
             selected_model = inquirer.select(
                message="Which brain do you want today?",
                choices=models,
                default="gemini-2.5-flash"
            ).execute()

        # --- Launch ---
        chat_model = ChatGoogleGenerativeAI(model=selected_model, api_key=os.environ["GEMINI_API_KEY"], streaming=True)
        agent = Agent(model=chat_model, history=start_history, user_id=user_id)
        
        start_session(agent, start_history, user_id)
        
    except Exception as e:
        console.print(f"[bold red]Something broke: {e}[/bold red]")
    finally:
        console.print("[dim]Shutting down the server...[/dim]")
        server_process.terminate()

if __name__ == "__main__":
    main()