"""
Simple in-memory store for the Application Tracker.
For MVP this is sufficient; swap with SQLite / PostgreSQL later.
"""
from typing import List, Dict
import uuid
from datetime import date

_applications: List[Dict] = []


def get_all() -> List[Dict]:
    return list(_applications)


def add_application(app: Dict) -> Dict:
    app["id"] = str(uuid.uuid4())
    _applications.append(app)
    return app


def update_status(app_id: str, status: str) -> Dict | None:
    for app in _applications:
        if app["id"] == app_id:
            app["status"] = status
            return app
    return None


def delete_application(app_id: str) -> bool:
    global _applications
    before = len(_applications)
    _applications = [a for a in _applications if a["id"] != app_id]
    return len(_applications) < before
