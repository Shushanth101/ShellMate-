import sqlite3
import bcrypt
import json
import os
from datetime import datetime
from pathlib import Path

# Where the magic happens (DB path)
BASE_DIR = Path(__file__).resolve().parent.parent 
DB_PATH = os.path.join(BASE_DIR, "shellmate.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    """Spinning up the tables if we don't have them."""
    conn = get_connection()
    c = conn.cursor()

    # The roster
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash BLOB NOT NULL,
            preferred_model TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # The archives
    c.execute('''
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT,
            content TEXT, -- Storing the whole convo as JSON
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    # The memory bank
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_facts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()

# --- User Management ---

def create_user(username, password, model="gemini-2.5-flash"):
    """Newcomer alert! Let's get them in the system."""
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute('INSERT INTO users (username, password_hash, preferred_model) VALUES (?, ?, ?)',
                  (username, password_hash, model))
        conn.commit()
        conn.close()
        return True, "Welcome aboard! User created."
    except sqlite3.IntegrityError:
        return False, "Taken! Pick another name."
    except Exception as e:
        return False, str(e)

def verify_user(username, password):
    """Checking ID. Are you who you say you are?"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT id, password_hash, preferred_model FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    conn.close()

    if user:
        user_id, stored_hash, model = user
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
            return user_id, model
    
    return None, None

def get_user_preferences(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT preferred_model FROM users WHERE id = ?', (user_id,))
    res = c.fetchone()
    conn.close()
    return res[0] if res else "gemini-2.5-flash"

# --- Chat History ---

def save_chat(user_id, messages, title_suggestion=None):
    """Stashing this convo for later."""
    # If we don't have a name, just stamp it with the time
    if not title_suggestion:
        title_suggestion = f"Chat at {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    messages_json = json.dumps(messages)
    
    conn = get_connection()
    c = conn.cursor()
    c.execute('INSERT INTO chats (user_id, title, content) VALUES (?, ?, ?)',
              (user_id, title_suggestion, messages_json))
    conn.commit()
    conn.close()

def get_user_chats(user_id):
    """List of all the times we hung out."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT id, title, created_at FROM chats WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
    chats = [{'id': r[0], 'title': r[1], 'date': r[2]} for r in c.fetchall()]
    conn.close()
    return chats

def get_chat_content(chat_id, user_id):
    """Digging deep into the archives for a specific memory."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT content FROM chats WHERE id = ? AND user_id = ?', (chat_id, user_id))
    res = c.fetchone()
    conn.close()
    return json.loads(res[0]) if res else None

# --- User Memory (Facts) ---

def store_user_fact(user_id, fact_content):
    """Writing this down in the permanent record."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('INSERT INTO user_facts (user_id, content) VALUES (?, ?)', (user_id, fact_content))
    conn.commit()
    conn.close()

def get_user_facts(user_id):
    """Recall everything we know about this person."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT content FROM user_facts WHERE user_id = ? ORDER BY created_at ASC', (user_id,))
    facts = [r[0] for r in c.fetchall()]
    conn.close()
    return "\n".join(facts)
