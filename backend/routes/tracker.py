from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.utils import store
from typing import Optional

router = APIRouter(prefix="/tracker", tags=["Tracker"])


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
    return store.add_application(app.model_dump())


@router.patch("/{app_id}/status")
def update_status(app_id: str, body: StatusUpdate):
    updated = store.update_status(app_id, body.status)
    if not updated:
        raise HTTPException(status_code=404, detail="Application not found")
    return updated


@router.delete("/{app_id}")
def delete_application(app_id: str):
    ok = store.delete_application(app_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Application not found")
    return {"deleted": True}
