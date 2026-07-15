import sys
import os
import msvcrt
import time
import uuid
from langchain.messages import HumanMessage

# Bootstrap project root into Python search path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.agents.orchestrator import agent

def clear_screen():
    # Enable ANSI escape processing on Windows
    os.system("")
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()

def get_terminal_size():
    try:
        size = os.get_terminal_size()
        return size.columns, size.lines
    except OSError:
        return 80, 24

def draw_tui_layout():
    cols, rows = get_terminal_size()
    # Set scrolling region to top (rows - 3) lines
    # DECSTBM: \033[<top>;<bottom>r
    sys.stdout.write(f"\033[1;{rows - 3}r")
    # Draw horizontal separator at row-2
    sys.stdout.write(f"\033[{rows - 2};1H\033[2K" + "-" * cols)
    # Draw horizontal separator at row
    sys.stdout.write(f"\033[{rows};1H\033[2K" + "-" * cols)
    # Move cursor to bottom of scroll region
    sys.stdout.write(f"\033[{rows - 3};1H")
    sys.stdout.flush()

def get_user_input():
    cols, rows = get_terminal_size()
    prompt = "you: "
    # Move cursor to rows-1, clear line, and print prompt
    sys.stdout.write(f"\033[{rows - 1};1H\033[2K{prompt}")
    sys.stdout.flush()
    
    user_input = []
    while True:
        if msvcrt.kbhit():
            ch = msvcrt.getwch()
            if ch == '\r' or ch == '\n': # Enter key
                break
            elif ch == '\x03': # Ctrl+C
                raise KeyboardInterrupt()
            elif ch == '\x08': # Backspace
                if user_input:
                    user_input.pop()
                    # Redraw prompt and current input
                    sys.stdout.write(f"\033[{rows - 1};1H\033[2K{prompt}{''.join(user_input)}")
                    sys.stdout.flush()
            elif ord(ch) >= 32: # Printable character
                user_input.append(ch)
                sys.stdout.write(ch)
                sys.stdout.flush()
        else:
            time.sleep(0.01)
            
    # Clear input prompt row when done
    sys.stdout.write(f"\033[{rows - 1};1H\033[2K")
    sys.stdout.flush()
    return "".join(user_input).strip()

def print_to_history(text):
    cols, rows = get_terminal_size()
    # Move to rows-3 (bottom of scroll region) and print
    sys.stdout.write(f"\033[{rows - 3};1H\n{text}\n")
    sys.stdout.flush()

def main():
    clear_screen()
    draw_tui_layout()
    
    print_to_history("=== Shellmate Agent (TUI Mode) ===")
    print_to_history("Type 'exit' or 'quit' to end the session.\n")
    
    config = {
        "configurable": {"thread_id": uuid.uuid4()}
    }
    
    current_cols, current_rows = get_terminal_size()
    
    try:
        while True:
            # Check for terminal resize before prompt
            cols, rows = get_terminal_size()
            if cols != current_cols or rows != current_rows:
                current_cols, current_rows = cols, rows
                draw_tui_layout()
            
            user_input = get_user_input()
            if not user_input:
                continue
            
            print_to_history(f"you: {user_input}")
            
            if user_input.lower() in ("exit", "quit"):
                print_to_history("Exiting...")
                break
            
            # Start streaming assistant response
            sys.stdout.write(f"\033[{rows - 3};1H\nAssistant: ")
            sys.stdout.flush()
            
            for chunk, metadata in agent.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=config,
                stream_mode="messages"
            ):
                # Stream AI text tokens
                if hasattr(chunk, "content") and isinstance(chunk.content, str) and chunk.content:
                    node = metadata.get("langgraph_node")
                    if node == "llm_call":
                        sys.stdout.write(chunk.content)
                        sys.stdout.flush()
                        
                        # Handle reasoning content safely
                        if chunk.additional_kwargs:
                            reasoning = getattr(chunk.additional_kwargs, "reasoning_content", None)
                            if not reasoning and isinstance(chunk.additional_kwargs, dict):
                                reasoning = chunk.additional_kwargs.get("reasoning_content")
                            if reasoning:
                                sys.stdout.write(str(reasoning))
                                sys.stdout.flush()
            
            # End of assistant response
            sys.stdout.write("\n")
            sys.stdout.flush()
            
    except KeyboardInterrupt:
        pass
    finally:
        # Reset scroll region back to full screen
        sys.stdout.write("\033[r")
        cols, rows = get_terminal_size()
        sys.stdout.write(f"\033[{rows};1H\n")
        sys.stdout.flush()
        print("Session ended.")

if __name__ == "__main__":
    main()