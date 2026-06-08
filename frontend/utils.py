import requests
import streamlit as st

BASE_URL = "http://localhost:8000"
API_BASE_URL = "https://careeros-ls09.onrender.com"



def api_post(endpoint: str, payload: dict) -> dict | None:
    """POST to FastAPI, return JSON or show error."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/analyze",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Cannot connect to backend. Run: `uvicorn backend.main:app --reload`")
    except requests.exceptions.HTTPError as e:
        st.error(f"API error {e.response.status_code}: {e.response.text}")
    except Exception as e:
        st.error(f"Unexpected error: {e}")
    return None


def api_get(endpoint: str) -> list | dict | None:
    try:
        resp = requests.get(f"{BASE_URL}{endpoint}", timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Cannot connect to backend. Run: `uvicorn backend.main:app --reload`")
    except Exception as e:
        st.error(f"Error: {e}")
    return None


def api_patch(endpoint: str, payload: dict) -> dict | None:
    try:
        resp = requests.patch(f"{BASE_URL}{endpoint}", json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"Error: {e}")
    return None


def api_delete(endpoint: str) -> bool:
    try:
        resp = requests.delete(f"{BASE_URL}{endpoint}", timeout=30)
        resp.raise_for_status()
        return True
    except Exception as e:
        st.error(f"Error: {e}")
    return False


def score_color(score: int) -> str:
    if score >= 75:
        return "🟢"
    elif score >= 55:
        return "🟡"
    return "🔴"


def status_emoji(status: str) -> str:
    return {
        "Applied": "📨",
        "OA": "💻",
        "Interview": "🎯",
        "Offer": "🎉",
        "Rejected": "❌",
    }.get(status, "📋")
