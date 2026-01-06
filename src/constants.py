import os

# Get the directory of the current file (src/)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to shellmate.db in the parent directory
DB_PATH = os.path.join(current_dir, '..', 'shellmate.db')

# Normalize the path to handle '..'
DB_PATH = os.path.abspath(DB_PATH)

# Other constants
welcome_messages = [
    "Hello there! How can I assist you today?",
    "Welcome back! Ready to code?",
    "ShellMate at your service! What's on your mind?",
    "Hey! Let's build something amazing."
]

models = [
    "gemini-2.5-flash",
    "gemini-1.5-pro-latest",
]

