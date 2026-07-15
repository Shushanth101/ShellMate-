# Shellmate v5

Shellmate is a robust, terminal-based AI coding harness agent built using [LangChain](https://github.com/langchain-ai/langchain) and [LangGraph](https://github.com/langchain-ai/langgraph), powered by Google Gemini (`gemini-2.5-flash`).

## Demo

<video src="https://github.com/Shushanth101/ShellMate-/raw/v5/shellmatev5.mp4" width="100%" controls></video>

## Features

- **Split-Screen Terminal UI (TUI)**: A clean terminal UI where conversation history scrolls in the top section and your input prompt (`you: `) remains pinned at the bottom between horizontal separators.
- **Persistent Shell Tooling**: Executes shell commands in a persistent PTY session, supporting interactive and long-running processes (linters, test suites, builds).
- **File System Operations**: Direct file read/write tools with absolute safety.
- **Web Navigation**: Built-in web search and webpage fetching capabilities to retrieve documentation and API guides.
- **Python REPL**: Sandboxed execution of Python snippets for validation, AST checks, and logic reproduction.

## Directory Structure

```text
├── src/
│   ├── agents/
│   │   └── orchestrator.py    # Main agent StateGraph and tool registrations
│   ├── prompts/
│   │   └── systemprompts.py   # Agent system instructions
│   ├── tools/
│   │   ├── shell_tool.py      # PTY persistent shell execution backend
│   │   └── tools.py           # Core agent tool definitions
│   └── main.py                # TUI event loop and CLI entrypoint
├── requirements.txt           # Project dependencies
└── .env                       # Environment configuration
```

## Setup & Installation

### 1. Prerequisites
- **Python 3.10+**
- **MongoDB**: A running local MongoDB instance on port `27017` is required for the agent checkpointer.

### 2. Install Dependencies
Create a virtual environment and install the required Python packages:
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the root directory:
```env
GOOGLE_API_KEY = your_google_gemini_api_key_here
OLLAMA_API_KEY = your_ollama_api_key_here # For web search/fetch
```

## How to Run

Launch the interactive Terminal UI:
```powershell
python src/main.py
```
Type your coding task or queries, and the agent will execute commands and edit code directly in your workspace. Use `exit` or `quit` to end the session.
