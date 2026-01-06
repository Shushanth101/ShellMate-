# ShellMate 🐚

ShellMate is an advanced AI CLI Companion designed to help you with coding, system tasks, and project management. It features persistent memory, user authentication, and chat history management.

## 🚀 How to Use

### 1. Installation
Ensure you have the dependencies installed:
```bash
pip install -r requirements.txt
```
*(Make sure to set up your `.env` with `GEMINI_API_KEY`)*

### 2. Authentication
ShellMate supports multiple users with private memories and chat histories.

- **Sign Up**: Register a new account.
  ```bash
  python src/main.py --signup --username <your_name> --password <your_password>
  ```

- **Login**: Start a session with your credentials.
  ```bash
  python src/main.py --login --username <your_name> --password <your_password>
  ```
  *Or simply run `python src/main.py` and select "Login" from the menu.*

- **Anonymous Mode**: Use without saving history.
  ```bash
  python src/main.py --anonymous
  ```

### 3. Chat Features
- **Save Chat**: Type `/save` during a conversation to persist it to the database. An AI-generated title will be assigned automatically.
- **Resume Chat**: view and resume past conversations.
  ```bash
  python src/main.py --chats
  ```

## 🏗️ Important Components

### `src/classes/AgentClass.py`
The core agent logic. It initializes the LangChain agent and binds tools.
- **Key Feature**: Uses a **closure** in `__init__` to securely bind the `store_user_facts` tool to the specific authenticated `user_id`.

### `src/database.py`
Handles all persistence using SQLite (`shellmate.db`).
- **Tables**: `users`, `chats`, `user_facts`.
- **Security**: Uses `bcrypt` for password hashing.

### `src/utils/system_prompt.py`
Generates the dynamic system prompt.
- **Dynamic Memory**: Fetches user-specific facts from the database and injects them into the prompt, giving the AI "Long-Term Memory".

### `src/main.py`
The entry point. Handles CLI arguments (`argparse`), authentication flow, and the main interactive chat loop.

## 📝 TODO & Roadmap

- [ ] **Implement Model Providers & Selection**:
    - Add support for Anthropic (Claude), OpenAI (GPT-4), and local models (Ollama).
    - Allow users to select their preferred provider/model via CLI flag (e.g., `--provider openai --model gpt-4`).
    - Store API keys securely or manage them via env vars.
- [ ] implement history(the history is not being fed to model...) 
