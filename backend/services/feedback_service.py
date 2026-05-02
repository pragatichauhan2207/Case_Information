# ============================================================
# services/feedback_service.py
# Simple in-memory feedback store.
# In a real app you'd swap this for a database (SQLite/Postgres).
# ============================================================

import uuid
from datetime import datetime

# In-memory list acts as our "database" for this demo
_feedback_store: list = []


def add_feedback(name: str, email: str, message: str) -> dict:
    """
    Save a new feedback entry and return it.
    """
    entry = {
        "id":         str(uuid.uuid4()),
        "name":       name.strip(),
        "email":      email.strip(),
        "message":    message.strip(),
        "created_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
    }
    _feedback_store.append(entry)
    return entry


def get_all_feedback() -> list:
    """Return all feedback entries (newest first)."""
    return list(reversed(_feedback_store))
