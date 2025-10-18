import os
import json
from datetime import datetime
from pathlib import Path
import platform
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
dotenv_path = BASE_DIR / ".env"
load_dotenv(dotenv_path)

db_enabled = os.getenv("ENABLE_DB_LOGGING", "false").lower() == "true"
DB_TYPE = os.getenv("DB_TYPE") if db_enabled else None



if db_enabled:
    try:
        if DB_TYPE == "mongodb":
            from pymongo import MongoClient

            MONGO_URI = os.getenv("MONGO_URI")
            DB_NAME = os.getenv("DB_NAME")
            client = MongoClient(MONGO_URI)
            db = client[DB_NAME]
            conversations_collection = db["conversations"]

        elif DB_TYPE == "postgresql":
            import psycopg2

            DB_HOST = os.getenv("DB_HOST")
            DB_PORT = os.getenv("DB_PORT")
            DB_NAME = os.getenv("DB_NAME")
            DB_USER = os.getenv("DB_USER")
            DB_PASSWORD = os.getenv("DB_PASSWORD")

            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )
            cursor = conn.cursor()

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id SERIAL PRIMARY KEY,
                session_id TEXT,
                user_input TEXT,
                agent_output TEXT,
                tools_used JSONB,
                timestamp TIMESTAMP,
                current_directory TEXT,
                os TEXT
            )
            """)
            conn.commit()

        else:
            raise ValueError("Unsupported DB_TYPE. Use 'mongodb' or 'postgresql'.")
    except Exception as e:
        print(f"[Warning] Database logging disabled: {e}")
        db_enabled = False  

def log_conversation(session_id: str, user_input: str, agent_output: str, tools_used: list):
    """
    Logs a conversation step to the configured database (MongoDB or PostgreSQL).

    Args:
        session_id (str): ID of the conversation session.
        user_input (str): User's input message.
        agent_output (str): Agent's response.
        tools_used (list): List of tools used in this step.
    """
    if not db_enabled:
        return

    tools_list = tools_used if isinstance(tools_used, list) else []
    cwd = os.getcwd()
    os_name = platform.system()
    timestamp = datetime.utcnow()

    try:
        if DB_TYPE == "mongodb":
            conversations_collection.insert_one({
                "session_id": session_id,
                "user_input": user_input,
                "agent_output": agent_output,
                "tools_used": tools_list,
                "timestamp": timestamp,
                "current_directory": cwd,
                "os": os_name
            })

        elif DB_TYPE == "postgresql":
            cursor.execute(
                """
                INSERT INTO conversations 
                (session_id, user_input, agent_output, tools_used, timestamp, current_directory, os) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (session_id, user_input, agent_output, json.dumps(tools_list),
                 timestamp, cwd, os_name)
            )
            conn.commit()

    except Exception as e:
        print(f"[Warning] Failed to log conversation: {e}")
