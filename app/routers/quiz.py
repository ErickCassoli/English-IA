from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.repo import dao, models
from app.repo.db import get_db
from app.schemas.quiz import QuizAnswerRequest, QuizAnswerResponse, QuizItemSchema, QuizListResponse

router = APIRouter(prefix="/api/quiz", tags=["quiz"])


def _decode_choices(quiz: models.Quiz) -> tuple[list[str], str | None]:
    data = json.loads(quiz.choices_json)
    if isinstance(data, dict):
        return list(data.get("choices", [])), data.get("source_error_id")
    return list(data), None


@router.get("/by-session/{session_id}", response_model=QuizListResponse)
def quiz_by_session(session_id: str, db: Session = Depends(get_db)):
    session = dao.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    quizzes = dao.list_quizzes_by_session(db, session_id)
    items: list[QuizItemSchema] = []
    for quiz in quizzes:
        choices, _ = _decode_choices(quiz)
        items.append(
            QuizItemSchema(
                id=quiz.id,
                type=quiz.type.value,
                prompt=quiz.prompt,
                choices=choices,
            )
        )
    return QuizListResponse(items=items)


@router.post("/{quiz_id}/answer", response_model=QuizAnswerResponse)
def answer_quiz(quiz_id: str, payload: QuizAnswerRequest, db: Session = Depends(get_db)):
    quiz = dao.get_quiz(db, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    user = dao.ensure_default_user(db)
    choice = payload.choice.strip()
    if not choice:
        raise HTTPException(status_code=400, detail="choice is required")
    is_correct = choice.lower() == quiz.answer.lower()
    dao.record_quiz_attempt(db, quiz, user, is_correct, payload.latency_ms)

    flashcard_created = False
    if not is_correct:
        _, source_error_id = _decode_choices(quiz)
        if source_error_id:
            error = db.get(models.ErrorSpan, source_error_id)
            if error:
                _, flashcard_created = dao.ensure_flashcard_from_error(
                    db, error, error.user_text, error.corrected_text
                )

    db.commit()
    return QuizAnswerResponse(quiz_id=quiz.id, is_correct=is_correct, flashcard_created=flashcard_created)
