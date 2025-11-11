from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.repo import dao, models
from app.repo.db import get_db
from app.schemas.session import SessionCreateRequest, SessionFinishResponse, SessionResponse
from app.services.evaluation import quizgen, report

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


def _to_response(session: models.Session) -> SessionResponse:
    return SessionResponse(
        id=session.id,
        topic=session.topic,
        status=session.status.value,
        started_at=session.started_at,
        ended_at=session.ended_at,
    )


@router.post("", response_model=SessionResponse)
def create_session(payload: SessionCreateRequest, db: Session = Depends(get_db)):
    user = dao.ensure_default_user(db)
    session = dao.create_session(db, user, payload.topic or "random")
    db.commit()
    db.refresh(session)
    return _to_response(session)


@router.post("/{session_id}/finish", response_model=SessionFinishResponse)
def finish_session(session_id: str, db: Session = Depends(get_db)):
    session = dao.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.status == models.SessionStatus.FINISHED:
        return SessionFinishResponse(quizzes_created=0, flashcards_created=0, report_ready=True)

    messages = dao.list_session_messages(db, session_id)
    errors = dao.list_session_errors(db, session_id)

    quiz_items = quizgen.generate_quiz(session.topic, errors)
    dao.create_quizzes(db, session, quiz_items)

    flashcards_created = 0
    for error in errors:
        _, created = dao.ensure_flashcard_from_error(db, error, error.user_text, error.corrected_text)
        if created:
            flashcards_created += 1

    report_data = report.build_report(messages, errors)
    dao.record_metric_snapshot(
        db,
        session.user,
        session,
        report_data["words"],
        report_data["errors"],
        report_data["accuracy_pct"],
        models.CEFRLevel(report_data["cefr"]),
    )
    dao.mark_session_finished(db, session)
    db.commit()

    return SessionFinishResponse(
        quizzes_created=len(quiz_items),
        flashcards_created=flashcards_created,
        report_ready=True,
    )
