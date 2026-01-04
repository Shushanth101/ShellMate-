import requests
import sys

BASE_URL = "http://127.0.0.1:5000"

class APIClient:
    def __init__(self):
        self.user_id = None
        self.session = requests.Session()
    
    def set_user(self, user_id):
        """Remember who we are talking to."""
        self.user_id = user_id
        self.session.headers.update({"X-User-ID": str(user_id)})

    def check_health(self):
        """Poke the server to see if it's awake."""
        try:
            r = self.session.get(f"{BASE_URL}/health", timeout=2)
            return r.status_code == 200
        except:
            return False

    def signup(self, username, password):
        """Knocking on the door with a new ID."""
        try:
            r = self.session.post(f"{BASE_URL}/auth/signup", json={"username": username, "password": password})
            return r.json()
        except Exception as e:
            return {"success": False, "message": str(e)}

    def login(self, username, password):
        """Trying to get past the bouncer."""
        try:
            r = self.session.post(f"{BASE_URL}/auth/login", json={"username": username, "password": password})
            if r.status_code == 200:
                data = r.json()
                self.set_user(data['user_id'])
                return data
            return {"success": False, "message": "Login failed"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def get_chats(self):
        """Fetch the history books."""
        r = self.session.get(f"{BASE_URL}/chats")
        if r.status_code == 200:
            return r.json()
        return []

    def save_chat(self, messages, title):
        """Archive this masterpiece."""
        r = self.session.post(f"{BASE_URL}/chats", json={"messages": messages, "title": title})
        return r.json()

    def get_chat_content(self, chat_id):
        """Pulling up an old conversation."""
        r = self.session.get(f"{BASE_URL}/chats/{chat_id}")
        if r.status_code == 200:
            return r.json()
        return None

    def get_facts(self):
        """What do we know?"""
        r = self.session.get(f"{BASE_URL}/facts")
        if r.status_code == 200:
            return r.json().get("facts", "")
        return ""

    def store_fact(self, fact):
        """Remember this for later."""
        r = self.session.post(f"{BASE_URL}/facts", json={"fact": fact})
        return r.json()

# Singleton instance for the app to use
client = APIClient()
