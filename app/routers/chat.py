from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.repo import dao, models
from app.repo.db import get_db
from app.schemas.chat import ChatMessageRequest, ChatMessageResponse, DetectedErrorSchema
from app.services.evaluation import errors as error_service
from app.services.llm import registry

router = APIRouter(prefix="/api/chat", tags=["chat"])


@lru_cache(maxsize=1)
def _system_prompt() -> str:
    prompt_path = Path(__file__).resolve().parents[2] / "prompts" / "tutor_roleplay.poml"
    if prompt_path.exists():
        return prompt_path.read_text(encoding="utf-8")
    return "You are a patient English tutor. Provide concise corrections."


def _serialize_errors(detected: list[error_service.DetectedError]) -> list[DetectedErrorSchema]:
    return [
        DetectedErrorSchema(
            start=err.start,
            end=err.end,
            category=err.category.value,
            user_text=err.user_text,
            corrected_text=err.corrected_text,
            note=err.note,
        )
        for err in detected
    ]


@router.post("/{session_id}/message", response_model=ChatMessageResponse)
def send_message(session_id: str, payload: ChatMessageRequest, db: Session = Depends(get_db)):
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="Text is required")
    session = dao.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.status != models.SessionStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Session is not active")

    user_message = dao.append_message(db, session, models.MessageRole.USER, payload.text.strip())
    detected_errors = error_service.detect_errors(payload.text)
    dao.save_error_spans(db, user_message, detected_errors)

    messages = dao.list_session_messages(db, session_id)
    history = [{"role": "system", "content": _system_prompt()}]
    for msg in messages[-6:]:
        history.append({"role": msg.role.value, "content": msg.text})

    settings_row = dao.get_settings(db)
    llm_client = registry.get_llm(settings_row)
    reply = llm_client.reply(history)
    dao.append_message(db, session, models.MessageRole.ASSISTANT, reply)
    db.commit()

    return ChatMessageResponse(reply=reply, detected_errors=_serialize_errors(detected_errors))
