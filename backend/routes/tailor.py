from fastapi import APIRouter
from pydantic import BaseModel
from backend.utils.gemini import call_gemini
from backend.exceptions import EmptyInputError, InputTooLongError, GeminiResponseParseError
import re

router = APIRouter(prefix="/tailor", tags=["Resume Tailor"])


class TailorRequest(BaseModel):
    target_role: str
    resume: str
    optimize_summary: bool = True
    optimize_skills: bool = True
    optimize_experience: bool = True
    optimize_projects: bool = False


class TailorResponse(BaseModel):
    optimized_summary: str
    optimized_skills: str
    optimized_experience: str
    optimized_projects: str
    tips: list[str]


@router.post("/", response_model=TailorResponse)
def tailor_resume(req: TailorRequest):
    if not req.target_role.strip() or not req.resume.strip():
        raise EmptyInputError(
            user_message="Please provide both a target role and your resume content."
        )
    if len(req.resume) > 20_000:
        raise InputTooLongError(
            user_message=(
                "Your resume is too long to process. "
                "Try pasting just the key sections (summary, skills, experience)."
            )
        )

    sections = [
        req.optimize_summary and "SUMMARY",
        req.optimize_skills and "SKILLS",
        req.optimize_experience and "EXPERIENCE",
        req.optimize_projects and "PROJECTS",
    ]

    sections_str = ", ".join(sections) if sections else "SUMMARY, SKILLS, EXPERIENCE"

    system = (
        "You are an elite resume writer. Optimize resumes to be compelling, "
        "authentic, and keyword-rich for the target role. Use strong action verbs "
        "and quantifiable achievements wherever possible."
    )

    prompt = f"""Rewrite the following resume sections ({sections_str}) optimized for this target role.

TARGET ROLE: {req.target_role}

ORIGINAL RESUME:
{req.resume}

Return EXACTLY in this format (even if a section was not requested, return an empty string for it):

OPTIMIZED_SUMMARY:
[rewritten summary paragraph, 3-4 sentences]

OPTIMIZED_SKILLS:
[rewritten skills section as comma-separated list]

OPTIMIZED_EXPERIENCE:
[rewritten experience bullets, each bullet starting with •]

OPTIMIZED_PROJECTS:
[rewritten projects section, each on a new line]

TIP_1: [quick win suggestion]
TIP_2: [quick win suggestion]
TIP_3: [quick win suggestion]
"""

    raw = call_gemini(prompt, system)

    def extract_block(key: str) -> str:
        pattern = rf"{key}:\n([\s\S]+?)(?=\n[A-Z_]+:|$)"
        m = re.search(pattern, raw)
        return m.group(1).strip() if m else ""


    def extract_line(key: str) -> str:
        m = re.search(rf"{key}:\s*(.+)", raw)
        return m.group(1).strip() if m else ""

    summary = extract_block("OPTIMIZED_SUMMARY")
    skills = extract_block("OPTIMIZED_SKILLS")
    experience = extract_block("OPTIMIZED_EXPERIENCE")
    projects = extract_block("OPTIMIZED_PROJECTS")

    if not any([summary, skills, experience, projects]):
        raise GeminiResponseParseError(
            user_message=(
                "The AI couldn't parse the resume sections. "
                "Try simplifying your resume text and submit again."
            )
        )

    return TailorResponse(
        optimized_summary=summary,
        optimized_skills=skills,
        optimized_experience=experience,
        optimized_projects=projects,
        tips=[t for t in [extract_line("TIP_1"), extract_line("TIP_2"), extract_line("TIP_3")] if t],
    )
