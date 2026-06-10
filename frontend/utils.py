import requests
import streamlit as st

BASE_URL = "https://careeros-ls09.onrender.com"

def _extract_user_message(response: requests.Response) -> str:
    """
    Pull `user_message` from a CareerOS error JSON response.
    Falls back to a generic message if the shape is unexpected.
    """
    try:
        body = response.json()
        # CareerOS errors return {user_message, error_code, detail}
        return body.get("user_message") or body.get("detail") or "An error occurred. Please try again."
    except Exception:
        return f"Server error ({response.status_code}). Please try again."


def api_post(endpoint: str, payload: dict) -> dict | None:
    try:
        resp = requests.post(f"{BASE_URL}{endpoint}", json=payload, timeout=60)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        st.error(
            "⚠️ Cannot reach the backend server. "
            "Make sure it's running: `uvicorn backend.main:app --reload`"
        )
    except requests.exceptions.Timeout:
        st.error(
            "⏱️ The request timed out — the AI is taking too long. "
            "Please try again."
        )
    except requests.exceptions.HTTPError as e:
        st.error(_extract_user_message(e.response))
    except Exception:
        st.error("Something went wrong. Please try again in a moment.")
    return None


def api_get(endpoint: str) -> list | dict | None:
    try:
        resp = requests.get(f"{BASE_URL}{endpoint}", timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        st.error(
            "⚠️ Cannot reach the backend server. "
            "Make sure it's running: `uvicorn backend.main:app --reload`"
        )
    except requests.exceptions.Timeout:
        st.error("⏱️ The request timed out. Please try again.")
    except requests.exceptions.HTTPError as e:
        st.error(_extract_user_message(e.response))
    except Exception:
        st.error("Something went wrong. Please try again in a moment.")
    return None


def api_patch(endpoint: str, payload: dict) -> dict | None:
    try:
        resp = requests.patch(f"{BASE_URL}{endpoint}", json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.HTTPError as e:
        st.error(_extract_user_message(e.response))
    except Exception:
        st.error("Something went wrong. Please try again in a moment.")
    return None


def api_delete(endpoint: str) -> bool:
    try:
        resp = requests.delete(f"{BASE_URL}{endpoint}", timeout=30)
        resp.raise_for_status()
        return True
    except requests.exceptions.HTTPError as e:
        st.error(_extract_user_message(e.response))
    except Exception:
        st.error("Something went wrong. Please try again in a moment.")
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
