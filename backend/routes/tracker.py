from fastapi import APIRouter
from pydantic import BaseModel
from backend.utils import store
from backend.exceptions import (
    ApplicationNotFoundError,
    DuplicateApplicationError,
    EmptyInputError,
    InvalidInputError,
)
from typing import Optional

router = APIRouter(prefix="/tracker", tags=["Tracker"])

VALID_STATUSES = {"Applied", "OA", "Interview", "Offer", "Rejected"}


class ApplicationIn(BaseModel):
    company: str
    role: str
    applied_date: str
    status: str = "Applied"
    match_score: Optional[int] = None
    next_action: Optional[str] = ""


class StatusUpdate(BaseModel):
    status: str


@router.get("/")
def list_applications():
    return store.get_all()


@router.post("/")
def add_application(app: ApplicationIn):
    if not app.company.strip() or not app.role.strip():
        raise EmptyInputError(
            user_message="Company name and role are required to add an application."
        )
    if app.status not in VALID_STATUSES:
        raise InvalidInputError(
            user_message=f"'{app.status}' is not a valid status. Choose from: {', '.join(sorted(VALID_STATUSES))}."
        )
    if app.match_score is not None and not (0 <= app.match_score <= 100):
        raise InvalidInputError(
            user_message="Match score must be a number between 0 and 100."
        )

    # Duplicate check (same company + role, case-insensitive)
    existing = store.get_all()
    for existing_app in existing:
        if (
            existing_app["company"].lower() == app.company.strip().lower()
            and existing_app["role"].lower() == app.role.strip().lower()
        ):
            raise DuplicateApplicationError()

    return store.add_application(app.model_dump())


@router.patch("/{app_id}/status")
def update_status(app_id: str, body: StatusUpdate):
    if body.status not in VALID_STATUSES:
        raise InvalidInputError(
            user_message=f"'{body.status}' is not a valid status. Choose from: {', '.join(sorted(VALID_STATUSES))}."
        )
    updated = store.update_status(app_id, body.status)
    if not updated:
        raise ApplicationNotFoundError()
    return updated


@router.delete("/{app_id}")
def delete_application(app_id: str):
    ok = store.delete_application(app_id)
    if not ok:
        raise ApplicationNotFoundError()
    return {"deleted": True}
