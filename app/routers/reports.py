from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.repo import dao
from app.repo.db import get_db
from app.schemas.report import ReportResponse
from app.services.evaluation import report as report_service

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/{session_id}", response_model=ReportResponse)
def get_report(session_id: str, db: Session = Depends(get_db)):
    session = dao.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if not dao.quizzes_completed(db, session):
        raise HTTPException(status_code=400, detail="Complete all quizzes before viewing the report.")
    messages = dao.list_session_messages(db, session_id)
    errors = dao.list_session_errors(db, session_id)
    attempts = dao.list_quiz_attempts_by_session(db, session_id)
    topic_label = session.topic.label if session.topic else session.topic_code
    data = report_service.build_report(topic_label, messages, errors, attempts)
    return ReportResponse(**data)
