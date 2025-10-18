# 🐚 ShellMate

**ShellMate is an intelligent terminal assistant that allows users to interact with AI directly from their command line. Powered by Gemini, it can answer queries, run terminal commands, manage files, read directories, and perform Google searches, providing contextual assistance while you work on your projects. With optional database logging, modular tools, and easy setup, ShellMate is designed to streamline your workflow, making it possible to access AI assistance from anywhere on your system without complicated installation or packaging.**

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

```python E:/shellmate-with-python/main.py```



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

- **Logs and DB features only work if ENABLE_DB_LOGGING=true in .env.**

- **Keep uv.lock in the repo to ensure reproducible dependency versions.**
