from fastapi import APIRouter
from pydantic import BaseModel
from backend.utils.gemini import call_gemini
from backend.exceptions import EmptyInputError, InvalidInputError
import re

router = APIRouter(prefix="/network", tags=["Networking"])

MSG_TYPES = {
    "linkedin": "LinkedIn connection request (max 300 characters, warm, specific, no buzzwords)",
    "recruiter": "cold recruiter outreach email (subject line + body, concise, value-focused)",
    "referral": "referral request message to someone at the company (warm, respectful, specific ask)",
    "followup": "follow-up message sent 7 days after applying (brief, adds value, subtle nudge)",
}


class NetworkRequest(BaseModel):
    message_type: str  # linkedin | recruiter | referral | followup
    recipient_name: str
    recipient_title: str
    company: str
    target_role: str
    your_background: str


class NetworkResponse(BaseModel):
    message: str
    subject: str  # for email types; empty string otherwise
    word_count: int
    tips: list[str]


@router.post("/", response_model=NetworkResponse)
def generate_network_message(req: NetworkRequest):
    if not req.recipient_name.strip() or not req.company.strip() or not req.target_role.strip():
        raise EmptyInputError(
            user_message="Recipient name, company, and target role are all required to generate a message."
        )
    if req.message_type not in MSG_TYPES:
        raise InvalidInputError(
            user_message=(
                f"'{req.message_type}' is not a valid message type. "
                "Choose from: linkedin, recruiter, referral, followup."
            )
        )
    msg_type_desc = MSG_TYPES.get(req.message_type, MSG_TYPES["linkedin"])

    system = (
        "You are an expert at professional networking. Write authentic, "
        "personalized outreach messages that get responses. Never write "
        "generic templates. Be specific, human, and concise."
    )

    prompt = f"""Write a {msg_type_desc}.

RECIPIENT: {req.recipient_name}, {req.recipient_title} at {req.company}
TARGET ROLE: {req.target_role}
MY BACKGROUND: {req.your_background}

Return EXACTLY in this format:

SUBJECT: [subject line if email, else leave blank]
MESSAGE:
[the full message text]

TIP_1: [one tip to improve response rate]
TIP_2: [one tip to improve response rate]
"""

    raw = call_gemini(prompt, system)

    subject_m = re.search(r"SUBJECT:\s*(.+)", raw)
    subject = subject_m.group(1).strip() if subject_m else ""

    msg_m = re.search(r"MESSAGE:\n([\s\S]+?)(?=\nTIP_|$)", raw)
    message = msg_m.group(1).strip() if msg_m else raw

    def extract_line(key: str) -> str:
        m = re.search(rf"{key}:\s*(.+)", raw)
        return m.group(1).strip() if m else ""

    tips = [t for t in [extract_line("TIP_1"), extract_line("TIP_2")] if t]

    return NetworkResponse(
        message=message,
        subject=subject,
        word_count=len(message.split()),
        tips=tips,
    )
