"""
CareerOS Custom Exceptions
--------------------------
Every exception class maps one failure scenario to:
  - a human-friendly `user_message`  →  shown on the Streamlit frontend
  - a short `error_code`             →  used for logging / programmatic handling
  - an HTTP `status_code`            →  returned to the frontend in the JSON response

HOW TO USE IN A ROUTE
---------------------
    from backend.exceptions import GeminiRateLimitError
    raise GeminiRateLimitError()

HOW TO CUSTOMISE A MESSAGE
--------------------------
    raise GeminiUnavailableError(
        user_message="Our AI service is currently down. Please try again in a few minutes."
    )

The global exception handler in main.py catches every CareerOSError subclass
and converts it into a clean JSON response — no stack traces reach the frontend.
"""

from __future__ import annotations


# ─────────────────────────────────────────────
# Base
# ─────────────────────────────────────────────

class CareerOSError(Exception):
    """Base class for all CareerOS application errors."""

    status_code: int = 500
    error_code: str = "INTERNAL_ERROR"
    default_message: str = (
        "Something went wrong on our end. Please try again in a moment."
    )

    def __init__(self, user_message: str | None = None) -> None:
        self.user_message = user_message or self.default_message
        super().__init__(self.user_message)


# ─────────────────────────────────────────────
# Gemini / AI layer errors
# ─────────────────────────────────────────────

class GeminiRateLimitError(CareerOSError):
    """Raised when the Gemini free-tier rate limit (15 RPM) is hit."""
    status_code = 429
    error_code = "GEMINI_RATE_LIMIT"
    default_message = (
        "You've hit the AI rate limit. "
        "Please wait 30–60 seconds and try again."
    )


class GeminiUnavailableError(CareerOSError):
    """Raised when the Gemini API is unreachable or returns a 5xx error."""
    status_code = 503
    error_code = "GEMINI_UNAVAILABLE"
    default_message = (
        "The AI service is temporarily unavailable. "
        "Please try again in a few minutes."
    )


class GeminiAuthError(CareerOSError):
    """Raised when the GEMINI_API_KEY is missing, invalid, or expired."""
    status_code = 401
    error_code = "GEMINI_AUTH_ERROR"
    default_message = (
        "AI service authentication failed. "
        "Please check that your GEMINI_API_KEY is set correctly in the .env file."
    )


class GeminiResponseParseError(CareerOSError):
    """Raised when Gemini returns a response that cannot be parsed into the expected format."""
    status_code = 502
    error_code = "GEMINI_PARSE_ERROR"
    default_message = (
        "The AI returned an unexpected response format. "
        "Please try again — rephrasing your input sometimes helps."
    )


class GeminiEmptyResponseError(CareerOSError):
    """Raised when Gemini returns an empty or blocked response."""
    status_code = 502
    error_code = "GEMINI_EMPTY_RESPONSE"
    default_message = (
        "The AI returned an empty response — this can happen if the content "
        "was filtered. Please rephrase your input and try again."
    )


# ─────────────────────────────────────────────
# Input validation errors
# ─────────────────────────────────────────────

class EmptyInputError(CareerOSError):
    """Raised when a required input field is blank or too short."""
    status_code = 422
    error_code = "EMPTY_INPUT"
    default_message = (
        "One or more required fields are empty. "
        "Please fill in all required inputs before submitting."
    )


class InputTooLongError(CareerOSError):
    """Raised when a user-provided input exceeds the allowed token budget."""
    status_code = 422
    error_code = "INPUT_TOO_LONG"
    default_message = (
        "Your input is too long for the AI to process. "
        "Please shorten your resume or job description and try again."
    )


class InvalidInputError(CareerOSError):
    """Raised for structurally invalid inputs (wrong type, bad format, etc.)."""
    status_code = 422
    error_code = "INVALID_INPUT"
    default_message = (
        "The input you provided doesn't look right. "
        "Please check the format and try again."
    )


# ─────────────────────────────────────────────
# Tracker / data store errors
# ─────────────────────────────────────────────

class ApplicationNotFoundError(CareerOSError):
    """Raised when a tracker operation references an application ID that doesn't exist."""
    status_code = 404
    error_code = "APPLICATION_NOT_FOUND"
    default_message = (
        "We couldn't find that application. "
        "It may have already been deleted — please refresh the tracker."
    )


class DuplicateApplicationError(CareerOSError):
    """Raised when the user tries to add a duplicate company+role combination."""
    status_code = 409
    error_code = "DUPLICATE_APPLICATION"
    default_message = (
        "You've already added an application for this company and role. "
        "You can update its status from the tracker instead."
    )


class TrackerStoreError(CareerOSError):
    """Raised when the in-memory store encounters an unexpected error."""
    status_code = 500
    error_code = "TRACKER_STORE_ERROR"
    default_message = (
        "There was a problem saving your application data. "
        "Please try again."
    )


# ─────────────────────────────────────────────
# Configuration / startup errors
# ─────────────────────────────────────────────

class MissingConfigError(CareerOSError):
    """Raised when a required environment variable (e.g. GEMINI_API_KEY) is absent."""
    status_code = 500
    error_code = "MISSING_CONFIG"
    default_message = (
        "A required configuration value is missing. "
        "Please ensure your .env file is set up correctly and restart the server."
    )
