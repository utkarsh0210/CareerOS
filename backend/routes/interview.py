from fastapi import APIRouter
from pydantic import BaseModel
from backend.utils.gemini import call_gemini
from backend.exceptions import EmptyInputError, InvalidInputError, GeminiResponseParseError
import re

router = APIRouter(prefix="/interview", tags=["Interview Coach"])

INTERVIEW_TYPES = {
    "technical": "technical (DSA, system design, coding concepts)",
    "behavioral": "behavioral (STAR method, situational, leadership)",
    "mixed": "mixed (both technical and behavioral)",
    "product": "product sense (product design, metrics, prioritization)",
}


class GenerateQuestionsRequest(BaseModel):
    role: str
    interview_type: str  # technical | behavioral | mixed | product
    jd_snippet: str = ""
    num_questions: int = 5


class GenerateQuestionsResponse(BaseModel):
    questions: list[str]


class EvaluateAnswerRequest(BaseModel):
    question: str
    answer: str
    role: str
    interview_type: str


class EvaluateAnswerResponse(BaseModel):
    score: int  # 0-10
    strengths: list[str]
    improvements: list[str]
    ideal_answer_hint: str
    overall_feedback: str


@router.post("/questions", response_model=GenerateQuestionsResponse)
def generate_questions(req: GenerateQuestionsRequest):
    if not req.role.strip():
        raise EmptyInputError(
            user_message="Please enter the role you are interviewing for."
        )
    if req.interview_type not in INTERVIEW_TYPES:
        raise InvalidInputError(
            user_message=(
                f"'{req.interview_type}' is not a valid interview type. "
                "Choose from: technical, behavioral, mixed, product."
            )
        )
    if not 1 <= req.num_questions <= 10:
        raise InvalidInputError(
            user_message="Number of questions must be between 1 and 10."
        )
    
    itype = INTERVIEW_TYPES.get(req.interview_type, INTERVIEW_TYPES["mixed"])

    prompt = f"""Generate exactly {req.num_questions} realistic {itype} interview questions for the role below.

ROLE: {req.role}
JD CONTEXT: {req.jd_snippet or "General software engineering position"}

Return ONLY a numbered list, one question per line. No explanations.
Example:
1. Question here
2. Question here
"""

    raw = call_gemini(prompt)
    questions = []
    for line in raw.strip().split("\n"):
        line = line.strip()
        if re.match(r"^\d+[\.\)]\s+", line):
            q = re.sub(r"^\d+[\.\)]\s+", "", line).strip()
            if q:
                questions.append(q)

    # fallback: just split by newline if numbering not detected
    if not questions:
        questions = [l.strip() for l in raw.split("\n") if len(l.strip()) > 20]

    if not questions:
        raise GeminiResponseParseError(
            user_message=(
                "The AI didn't return any interview questions. "
                "Try being more specific about the role and try again."
            )
        )

    return GenerateQuestionsResponse(questions=questions[: req.num_questions])


@router.post("/evaluate", response_model=EvaluateAnswerResponse)
def evaluate_answer(req: EvaluateAnswerRequest):
    if not req.question.strip() or not req.answer.strip():
        raise EmptyInputError(
            user_message="Both a question and your answer are required for evaluation."
        )
    if len(req.answer.strip()) < 20:
        raise InvalidInputError(
            user_message=(
                "Your answer is too short to evaluate meaningfully. "
                "Please write a more detailed response."
            )
        )
    
    itype = INTERVIEW_TYPES.get(req.interview_type, INTERVIEW_TYPES["mixed"])

    system = (
        "You are a senior engineering interviewer. Evaluate candidate answers "
        "honestly but encouragingly. Be specific and actionable."
    )

    prompt = f"""Evaluate this interview answer for a {req.role} position ({itype} interview).

QUESTION: {req.question}

CANDIDATE'S ANSWER: {req.answer}

Return EXACTLY in this format:

SCORE: [integer 1-10]
STRENGTH_1: [specific thing done well]
STRENGTH_2: [specific thing done well]
IMPROVEMENT_1: [specific gap or missing element]
IMPROVEMENT_2: [specific gap or missing element]
IDEAL_HINT: [one sentence on what a 10/10 answer would include]
OVERALL: [2-3 sentence overall feedback, encouraging tone]
"""

    raw = call_gemini(prompt, system)

    def extract(key: str) -> str:
        m = re.search(rf"{key}:\s*(.+)", raw)
        return m.group(1).strip() if m else ""

    try:
        score = int(extract("SCORE") or "6")
    except ValueError:
        raise GeminiResponseParseError()

    return EvaluateAnswerResponse(
        score=max(1, min(10, score)),
        strengths=[s for s in [extract("STRENGTH_1"), extract("STRENGTH_2")] if s],
        improvements=[s for s in [extract("IMPROVEMENT_1"), extract("IMPROVEMENT_2")] if s],
        ideal_answer_hint=extract("IDEAL_HINT"),
        overall_feedback=extract("OVERALL"),
    )