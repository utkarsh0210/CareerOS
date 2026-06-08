import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# gemini-1.5-flash is free tier (as of 2025)
_model = genai.GenerativeModel("gemini-2.5-flash")


def call_gemini(prompt: str, system: str = "") -> str:
    """
    Call Gemini 1.5 Flash (free tier) with an optional system instruction.
    Returns the text response as a plain string.
    """
    full_prompt = f"{system}\n\n{prompt}" if system else prompt
    response = _model.generate_content(full_prompt)
    return response.text.strip()
