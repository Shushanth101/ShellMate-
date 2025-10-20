# 🐚 ShellMate

**ShellMate is an intelligent terminal assistant that allows users to interact with AI directly from their command line. Powered by Gemini, it can answer queries, run terminal commands, manage files(read and write to files), read directories, and perform Google searches, providing contextual assistance while you work on your projects. With optional database logging, modular tools, and easy setup, ShellMate is designed to streamline your workflow, making it possible to access AI assistance from anywhere on your system without complicated installation or packaging.**

---

## ⚙️ Requirements

- Python 3.12 or above
- Dependencies are listed in `pyproject.toml` and locked in `uv.lock` (if using PDM).  
  Install them with:

```bash
pip install .
```


Keeping uv.lock ensures everyone gets the exact same dependency versions.

ShellMate-/

├── .env

├── .python-version

├── .venv/

├── dblogging.py

├── gemini.py

├── main.py

├── pyproject.toml

├── README.md

├── system_prompt.py

├── tools.py

├── uv.lock

└── __pycache__/


⚡ Running ShellMate

You can run ShellMate from any folder without packaging:

```bash
python path/to/the/shellmate/porject

example:
python E:/ShellMate-/main.py
```



***Python automatically includes the folder containing main.py in its module search path, so all imports (tools, dblogging, system_prompt, etc.) will work correctly.***


## 🔧 Environment Setup

**1) Copy .env.example to .env:**

**2) Set your API key and any DB settings in .env:**



# 💡 Features


- **Chat with Gemini AI from the terminal**

- **Optional database logging (PostgreSQL or MongoDB)**

- **Modular design: tools.py, dblogging.py, system_prompt.py**

- **Easy to run from anywhere on your system**


##  Notes

- **Your current working directory does not matter when running main.py using the full path.**

- **Ensure your Python environment has all dependencies installed.**

- **ENABLE_DB_LOGGING — if set to true, ShellMate will send chats to the configured database (PostgreSQL or MongoDB) for storage. Set to false to skip sending chats. Chats are not stored if set to false**

- **Keep uv.lock in the repo to ensure reproducible dependency versions.**


## MongoDB Schema

**MongoDB is schemaless, but your documents will have the following fields:**
```json
{
  "session_id": "<string>",          
  "user_input": "<string>",          
  "agent_output": "<string>",        
  "tools_used": ["<string>", ...],   
  "timestamp": "<datetime>",         
  "current_directory": "<string>",   
  "os": "<string>"                   
}
```

**Collection: `conversations`**

---

## PostgreSQL Schema

**For PostgreSQL, the equivalent table can be defined like this:**

```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    user_input TEXT NOT NULL,
    agent_output TEXT NOT NULL,
    tools_used JSONB,            
    timestamp TIMESTAMP NOT NULL,
    current_directory TEXT,
    os VARCHAR(50)
);
```
- **tools_used is stored as JSONB to preserve the array structure.**

- **timestamp stores when the conversation occurred.**

- **session_id can be used to group messages belonging to the same session.**



## Demo Videos 🎥:

https://github.com/user-attachments/assets/615c52d9-a2cd-4226-8084-43d3768fceaf

https://github.com/user-attachments/assets/32761f1e-9bf4-4e44-b1d1-faeb136d6e97





