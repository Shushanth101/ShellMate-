from flask import Flask, request, jsonify
import database as db
import os
from functools import wraps

app = Flask(__name__)

# Make sure the brain (DB) is hooked up
db.init_db()

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # We're just checking for an ID tag here. 
        # In the real world, we'd want tokens, but this works for now.
        user_id = request.headers.get("X-User-ID")
        if not user_id:
            return jsonify({"error": "Who are you? (Unauthorized)"}), 401
        return f(user_id, *args, **kwargs)
    return decorated

@app.route('/health', methods=['GET'])
def health():
    # Pulse check.
    return jsonify({"status": "ok"})

@app.route('/auth/signup', methods=['POST'])
def signup():
    # New friend incoming!
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({"success": False, "message": "Can't sign you up without a name and password."}), 400
    
    success, msg = db.create_user(username, password)
    if success:
        return jsonify({"success": True, "message": msg})
    else:
        return jsonify({"success": False, "message": msg}), 400

@app.route('/auth/login', methods=['POST'])
def login():
    # Knock knock.
    data = request.json
    username = data.get('username')
    password = data.get('password')
    user_id, model = db.verify_user(username, password)
    
    if user_id:
        return jsonify({"success": True, "user_id": user_id, "model": model})
    else:
        return jsonify({"success": False, "message": "Nope, wrong keys."}), 401

@app.route('/chats', methods=['GET'])
@require_auth
def list_chats(user_id):
    # Let's see what you've been talking about.
    chats = db.get_user_chats(user_id)
    return jsonify(chats)

@app.route('/chats', methods=['POST'])
@require_auth
def save_chat(user_id):
    # Saving this conversation for posterity.
    data = request.json
    messages = data.get('messages')
    title = data.get('title')
    
    if not messages or not title:
        return jsonify({"success": False, "message": "Can't save nothing."}), 400
        
    db.save_chat(user_id, messages, title)
    return jsonify({"success": True, "message": "Got it. Saved."})

@app.route('/chats/<int:chat_id>', methods=['GET'])
@require_auth
def get_chat(user_id, chat_id):
    # Digging up the archives.
    content = db.get_chat_content(chat_id, user_id)
    if content is not None:
        return jsonify(content)
    else:
        return jsonify({"error": "Couldn't find that chat."}), 404

@app.route('/facts', methods=['GET'])
@require_auth
def get_facts(user_id):
    # What do we know about you?
    facts = db.get_user_facts(user_id)
    return jsonify({"facts": facts})

@app.route('/facts', methods=['POST'])
@require_auth
def store_fact(user_id):
    # Learning something new.
    data = request.json
    fact = data.get('fact')
    if not fact:
        return jsonify({"success": False}), 400
    
    db.store_user_fact(user_id, fact)
    return jsonify({"success": True})

if __name__ == '__main__':
    # Let's get this party started on port 5000.
    app.run(host='127.0.0.1', port=5000, debug=False)
