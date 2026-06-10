import os
import google.generativeai as genai
from dotenv import load_dotenv
from backend.exceptions import (
    GeminiAuthError,
    GeminiRateLimitError,
    GeminiUnavailableError,
    GeminiEmptyResponseError,
    MissingConfigError,
)

load_dotenv()

_api_key = os.getenv("GEMINI_API_KEY")
if not _api_key:
    raise MissingConfigError(
        user_message=(
            "GEMINI_API_KEY is not set. "
            "Copy .env.example to .env and add your key from https://aistudio.google.com/app/apikey"
        )
    )

genai.configure(api_key=_api_key)
_model = genai.GenerativeModel("gemini-2.5-flash")


def call_gemini(prompt: str, system: str = "") -> str:
    """
    Call Gemini 1.5 Flash and return the response text.
    Raises a CareerOSError subclass on every known failure mode
    so the global handler can return a clean JSON error to the frontend.
    """
    full_prompt = f"{system}\n\n{prompt}" if system else prompt

    try:
        response = _model.generate_content(full_prompt)

        # Gemini can return a response with no candidates (e.g. safety-filtered)
        if not response.text or not response.text.strip():
            raise GeminiEmptyResponseError()

        return response.text.strip()

    except GeminiEmptyResponseError:
        raise  # already a CareerOSError — let it propagate

    except Exception as exc:
        err_str = str(exc).lower()

        if "api_key" in err_str or "api key" in err_str or "401" in err_str or "403" in err_str:
            raise GeminiAuthError() from exc

        if "quota" in err_str or "rate" in err_str or "429" in err_str or "resource_exhausted" in err_str:
            raise GeminiRateLimitError() from exc

        if any(k in err_str for k in ("503", "502", "unavailable", "timeout", "deadline")):
            raise GeminiUnavailableError() from exc

        # Unknown Gemini error — wrap as unavailable so frontend gets a clean message
        raise GeminiUnavailableError(
            user_message=(
                "The AI service encountered an unexpected error. "
                "Please try again in a moment."
            )
        ) from exc