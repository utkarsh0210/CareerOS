from fastapi import APIRouter
from pydantic import BaseModel
from backend.utils.gemini import call_gemini
from backend.exceptions import EmptyInputError, GeminiResponseParseError
import re

router = APIRouter(prefix="/analyze", tags=["JD Analyzer"])


class AnalyzeRequest(BaseModel):
    job_description: str
    resume: str


class AnalyzeResponse(BaseModel):
    match_score: int
    shortlist_likelihood: str
    matching_skills: list[str]
    missing_skills: list[str]
    suggestions: list[str]
    key_observation: str


@router.post("/", response_model=AnalyzeResponse)
def analyze_jd(req: AnalyzeRequest):

    if not req.job_description.strip() or not req.resume.strip():
        raise EmptyInputError(
            user_message="Please provide both a job description and your resume before analyzing."
        )
    if len(req.job_description) + len(req.resume) > 30_000:
        from backend.exceptions import InputTooLongError
        raise InputTooLongError()
    
    system = (
        "You are an expert ATS analyst and HR professional. "
        "Analyse a resume against a job description. "
        "Return ONLY the structured format requested — no extra commentary."
    )

    prompt = f"""Analyse this resume against the job description and return EXACTLY this format:

MATCH_SCORE: [integer 0-100]
SHORTLIST_LIKELIHOOD: [Low | Medium | High]
MATCHING_SKILLS: [comma-separated, 4-6 items]
MISSING_SKILLS: [comma-separated, 3-5 items]
SUGGESTION_1: [one concise, actionable improvement]
SUGGESTION_2: [one concise, actionable improvement]
SUGGESTION_3: [one concise, actionable improvement]
KEY_OBSERVATION: [one sentence insight about the overall fit]

JOB DESCRIPTION:
{req.job_description}

RESUME:
{req.resume}
"""

    raw = call_gemini(prompt, system)

    def extract(key: str) -> str:
        m = re.search(rf"{key}:\s*(.+)", raw)
        return m.group(1).strip() if m else ""

    try:
        match_score = int(extract("MATCH_SCORE") or "60")
    except ValueError:
        raise GeminiResponseParseError()
    
    shortlist = extract("SHORTLIST_LIKELIHOOD") or "Medium"
    matching = [s.strip() for s in extract("MATCHING_SKILLS").split(",") if s.strip()]
    missing = [s.strip() for s in extract("MISSING_SKILLS").split(",") if s.strip()]
    suggestions = [
        s for s in [extract("SUGGESTION_1"), extract("SUGGESTION_2"), extract("SUGGESTION_3")] if s
    ]
    observation = extract("KEY_OBSERVATION")

    if not matching and not missing and not observation:
        raise GeminiResponseParseError()

    return AnalyzeResponse(
        match_score=max(0, min(100, match_score)),
        shortlist_likelihood=shortlist,
        matching_skills=matching,
        missing_skills=missing,
        suggestions=suggestions,
        key_observation=observation,
    )
