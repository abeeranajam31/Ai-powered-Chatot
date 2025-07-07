from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()  # Load .env vars

client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
db = client["chatbot"]
history_col = db["history"]

def save_message(session_id, role, content):
    """Store a single message."""
    history_col.insert_one({"session_id": session_id, "role": role, "content": content})

def get_history(session_id):
    """Get all messages for a session, sorted by order of insertion."""
    return list(history_col.find({"session_id": session_id}).sort("_id", 1))

def delete_history(session_id):
    """(Optional) Clear history for a session."""
    history_col.delete_many({"session_id": session_id})
