from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Sequence

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.repo import models
from app.services.evaluation.errors import DetectedError
from app.services.evaluation.quizgen import QuizPayload
from app.utils.config import get_settings as get_runtime_settings

DEFAULT_USER_NICKNAME = "Local Learner"
runtime_settings = get_runtime_settings()


def ensure_default_user(db: Session) -> models.User:
    user = db.execute(select(models.User).limit(1)).scalar_one_or_none()
    if user:
        return user
    user = models.User(nickname=DEFAULT_USER_NICKNAME)
    db.add(user)
    db.flush()
    return user


def get_settings(db: Session) -> models.Settings:
    settings = db.get(models.Settings, 1)
    if settings:
        return settings
    settings = models.Settings(
        id=1,
        llm_provider=models.LLMProvider(runtime_settings.default_llm_provider),
        llm_model=runtime_settings.default_llm_model,
    )
    db.add(settings)
    db.flush()
    return settings


def update_settings(db: Session, provider: models.LLMProvider, llm_model: str) -> models.Settings:
    settings = get_settings(db)
    settings.llm_provider = provider
    settings.llm_model = llm_model
    settings.updated_at = datetime.now(tz=UTC)
    db.add(settings)
    db.flush()
    return settings


def create_session(db: Session, user: models.User, topic: str) -> models.Session:
    session = models.Session(user=user, topic=topic or "random")
    db.add(session)
    db.flush()
    return session


def get_session(db: Session, session_id: str) -> models.Session | None:
    return db.get(models.Session, session_id)


def mark_session_finished(db: Session, session: models.Session) -> None:
    session.status = models.SessionStatus.FINISHED
    session.ended_at = datetime.now(tz=UTC)
    db.add(session)


def append_message(db: Session, session: models.Session, role: models.MessageRole, text: str) -> models.Message:
    message = models.Message(session=session, role=role, text=text)
    db.add(message)
    db.flush()
    return message


def save_error_spans(db: Session, message: models.Message, errors: Sequence[DetectedError]) -> list[models.ErrorSpan]:
    spans: list[models.ErrorSpan] = []
    for error in errors:
        span = models.ErrorSpan(
            message=message,
            start=error.start,
            end=error.end,
            category=error.category,
            user_text=error.user_text,
            corrected_text=error.corrected_text,
            note=error.note,
        )
        db.add(span)
        spans.append(span)
    db.flush()
    return spans


def list_session_messages(db: Session, session_id: str) -> list[models.Message]:
    stmt: Select[tuple[models.Message]] = (
        select(models.Message).where(models.Message.session_id == session_id).order_by(models.Message.ts.asc())
    )
    return list(db.scalars(stmt))


def list_session_errors(db: Session, session_id: str) -> list[models.ErrorSpan]:
    stmt: Select[tuple[models.ErrorSpan]] = (
        select(models.ErrorSpan)
        .join(models.Message)
        .where(models.Message.session_id == session_id)
        .order_by(models.ErrorSpan.id.asc())
    )
    return list(db.scalars(stmt))


def create_quizzes(db: Session, session: models.Session, items: Sequence[QuizPayload]) -> list[models.Quiz]:
    quizzes: list[models.Quiz] = []
    for item in items:
        encoded = json.dumps({"choices": item.choices, "source_error_id": item.source_error_id})
        quiz = models.Quiz(
            session=session,
            type=item.type,
            prompt=item.prompt,
            choices_json=encoded,
            answer=item.answer,
        )
        db.add(quiz)
        quizzes.append(quiz)
    db.flush()
    return quizzes


def list_quizzes_by_session(db: Session, session_id: str) -> list[models.Quiz]:
    stmt = select(models.Quiz).where(models.Quiz.session_id == session_id).order_by(models.Quiz.created_at.asc())
    return list(db.scalars(stmt))


def get_quiz(db: Session, quiz_id: str) -> models.Quiz | None:
    return db.get(models.Quiz, quiz_id)


def record_quiz_attempt(db: Session, quiz: models.Quiz, user: models.User, is_correct: bool, latency_ms: int):
    attempt = models.QuizAttempt(quiz=quiz, user=user, is_correct=is_correct, latency_ms=latency_ms)
    db.add(attempt)
    db.flush()
    return attempt


def ensure_flashcard_from_error(
    db: Session, error: models.ErrorSpan, front: str, back: str
) -> tuple[models.Flashcard, bool]:
    stmt = select(models.Flashcard).where(models.Flashcard.source_error_id == error.id).limit(1)
    card = db.execute(stmt).scalar_one_or_none()
    if card:
        return card, False
    card = models.Flashcard(front=front, back=back, source_error=error)
    db.add(card)
    db.flush()
    return card, True


def list_flashcards_due(db: Session, limit: int = 20) -> list[models.Flashcard]:
    stmt = (
        select(models.Flashcard)
        .where(models.Flashcard.due_at <= datetime.now(tz=UTC))
        .order_by(models.Flashcard.due_at.asc())
        .limit(limit)
    )
    return list(db.scalars(stmt))


def update_flashcard_state(
    db: Session, card: models.Flashcard, reps: int, interval: int, ease: float, due_at: datetime
) -> models.Flashcard:
    card.reps = reps
    card.interval = interval
    card.ease = ease
    card.due_at = due_at
    db.add(card)
    db.flush()
    return card


def record_metric_snapshot(
    db: Session,
    user: models.User,
    session: models.Session,
    words: int,
    errors: int,
    accuracy_pct: float,
    cefr: models.CEFRLevel,
) -> models.MetricSnapshot:
    snapshot = models.MetricSnapshot(
        user=user,
        session=session,
        words=words,
        errors=errors,
        accuracy_pct=accuracy_pct,
        cefr_estimate=cefr,
    )
    db.add(snapshot)
    db.flush()
    return snapshot


def get_dashboard_summary(db: Session):
    last_session_stmt = (
        select(models.Session)
        .where(models.Session.ended_at.is_not(None))
        .order_by(models.Session.ended_at.desc())
        .limit(1)
    )
    last_session = db.execute(last_session_stmt).scalar_one_or_none()

    sessions_total = db.scalar(select(func.count(models.Session.id))) or 0
    quizzes_total = db.scalar(select(func.count(models.Quiz.id))) or 0
    flashcards_total = db.scalar(select(func.count(models.Flashcard.id))) or 0
    due_count = (
        db.scalar(
            select(func.count(models.Flashcard.id)).where(models.Flashcard.due_at <= datetime.now(tz=UTC))
        )
        or 0
    )

    return {
        "last_session": {
            "id": last_session.id if last_session else None,
            "topic": last_session.topic if last_session else None,
            "ended_at": last_session.ended_at.isoformat() if last_session and last_session.ended_at else None,
        },
        "totals": {
            "sessions": sessions_total,
            "quizzes": quizzes_total,
            "flashcards": flashcards_total,
        },
        "due_count": due_count,
    }
