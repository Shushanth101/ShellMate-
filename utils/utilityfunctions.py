import time
import shutil
from pyfiglet import figlet_format
from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.formatted_text import HTML
from rich.text import Text
import difflib

def typewriter_effect(text,delay=0.01):
    """Old school typing vibes."""
    for char in text:
        print(char,end="",flush=True)
        time.sleep(delay)

def rgb(r, g, b, text):
    return f"\033[38;2;{r};{g};{b}m{text}\033[0m"

def gradient_banner(text, font="ansi_shadow", start=(0,120,255), end=(0,255,100)):
    """
    Making things look cool with a gradient.
    start = blue  (R,G,B)
    end   = green (R,G,B)
    """
    cols = shutil.get_terminal_size().columns

    ascii_art = figlet_format(text, font=font).split("\n")
    lines_out = []

    for line in ascii_art:
        colored_line = ""
        length = len(line)

        for i, ch in enumerate(line):
            # Mixing up the colors (Linear interpolation for RGB)
            r = int(start[0] + (end[0] - start[0]) * (i / max(1, length)))
            g = int(start[1] + (end[1] - start[1]) * (i / max(1, length)))
            b = int(start[2] + (end[2] - start[2]) * (i / max(1, length)))

            colored_line += rgb(r, g, b, ch)

        lines_out.append(colored_line.center(cols))

    return "\n".join(lines_out)



def multiline_prompt(placeholder="ask shelly..."):
    """
    The main input box.
    """

    kb = KeyBindings()

    @kb.add("c-t")
    def _(event):
        # Ctrl+T sends the message
        event.app.exit(result=event.app.current_buffer.text)

    session = PromptSession(multiline=True, key_bindings=kb)

    with patch_stdout():
        text = session.prompt(
            HTML('<ansigreen><b>You ></b></ansigreen> ')
        )

    return text


def generate_rich_diff(old: str, new: str, path: str) -> Text:
    """Showing what changed, Git style."""
    old_lines = old.splitlines(keepends=True)
    new_lines = new.splitlines(keepends=True)

    diff = difflib.unified_diff(
        old_lines,
        new_lines,
        fromfile=f"a/{path}",
        tofile=f"b/{path}",
        lineterm=""
    )

    rich_text = Text()

    for line in diff:
        if line.startswith("+") and not line.startswith("+++"):
            rich_text.append(line, style="bold green")
        elif line.startswith("-") and not line.startswith("---"):
            rich_text.append(line, style="bold red")
        elif line.startswith("@@"):
            rich_text.append(line, style="bold yellow")
        else:
            rich_text.append(line, style="white")

    return rich_text