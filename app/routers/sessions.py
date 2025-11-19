from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.repo import dao, models
from app.repo.db import get_db
from app.schemas.session import SessionCreateRequest, SessionFinishResponse, SessionResponse
from app.services.evaluation import quizgen, report

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@lru_cache(maxsize=1)
def _base_system_prompt() -> str:
    prompt_path = Path(__file__).resolve().parents[2] / "prompts" / "tutor_roleplay.poml"
    if prompt_path.exists():
        return prompt_path.read_text(encoding="utf-8").strip()
    return "You are a patient English tutor helping the learner practice real-life conversations."


def _build_prompt(topic: models.PracticeTopic) -> str:
    base = _base_system_prompt()
    return (
        f"{base}\n\n"
        f"Conversation theme: {topic.label}.\n"
        f"Context: {topic.description}\n"
        "Keep the dialogue in English, ask follow-up questions, and surface gentle corrections."
    )


def _to_response(session: models.Session, topic: models.PracticeTopic) -> SessionResponse:
    return SessionResponse(
        session_id=session.id,
        topic_code=topic.code,
        topic_label=topic.label,
        topic_description=topic.description,
        system_prompt=session.system_prompt,
        status=session.status.value,
        started_at=session.started_at,
        ended_at=session.ended_at,
    )


@router.post("", response_model=SessionResponse)
def create_session(payload: SessionCreateRequest, db: Session = Depends(get_db)):
    user = dao.ensure_default_user(db)
    topic = None
    if payload.topic_code:
        requested_code = payload.topic_code.strip().lower()
        topic = dao.get_practice_topic_by_code(db, requested_code)
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
    if not topic:
        topic = dao.get_random_practice_topic(db)
    if not topic:
        raise HTTPException(status_code=500, detail="No practice topics configured")
    system_prompt = _build_prompt(topic)
    session = dao.create_session(db, user, topic, system_prompt)
    db.commit()
    db.refresh(session)
    return _to_response(session, topic)


@router.post("/{session_id}/finish", response_model=SessionFinishResponse)
def finish_session(session_id: str, db: Session = Depends(get_db)):
    session = dao.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.status == models.SessionStatus.FINISHED:
        return SessionFinishResponse(quizzes_created=0, flashcards_created=0, report_ready=True)

    messages = dao.list_session_messages(db, session_id)
    errors = dao.list_session_errors(db, session_id)

    topic_label = session.topic.label if session.topic else session.topic_code
    quiz_items = quizgen.generate_quiz(topic_label, errors)
    dao.create_quizzes(db, session, quiz_items)

    flashcards_created = 0
    for error in errors:
        _, created = dao.ensure_flashcard_from_error(db, error, error.user_text, error.corrected_text)
        if created:
            flashcards_created += 1

    report_data = report.build_report(topic_label, messages, errors)
    dao.record_metric_snapshot(
        db,
        session.user,
        session,
        report_data["kpis"]["words"],
        report_data["kpis"]["errors"],
        report_data["kpis"]["accuracy_pct"],
        models.CEFRLevel(report_data["kpis"]["cefr_estimate"]),
    )
    dao.mark_session_finished(db, session)
    db.commit()

    return SessionFinishResponse(
        quizzes_created=len(quiz_items),
        flashcards_created=flashcards_created,
        report_ready=True,
    )
