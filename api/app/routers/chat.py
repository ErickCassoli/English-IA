from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.repo import dao, models
from app.repo.db import get_db
from app.schemas.chat import ChatMessageRequest, ChatMessageResponse, DetectedErrorSchema, ChatHistoryItem
from app.services.evaluation import errors as error_service
from app.services.llm import registry
from app.utils.config import get_settings

"""
Chat Router
===========

Handles all real-time conversational interactions between the user and the AI Tutor.
This module manages message persistence, error detection pipelines, and LLM responses.

Endpoints:
    - POST /message: Send a user message and get a response + corrections.
    - GET  /history: Retrieve past messages for the session.
"""

router = APIRouter(prefix="/api/chat", tags=["chat"])
runtime_config = get_settings()


from app.utils.prompts import poml

@lru_cache(maxsize=1)
def _fallback_prompt() -> str:
    prompt_path = Path(__file__).resolve().parents[2] / "prompts" / "tutor_roleplay.poml"
    try:
        # Default fallback variables if loaded directly as fallback
        return poml.load(prompt_path, variables={"topic_label": "General", "topic_description": "Free conversation"})
    except:
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
    """
    Process a new user message in an active session.

    This endpoint performs three key actions:
    1. Saves the user's message to the database.
    2. Runs an asynchronous error detection pipeline (Grammar/Vocab/Fluency).
    3. Generates an AI response using the configured Tutor Persona (LLM).

    Args:
        session_id (str): The UUID of the active session.
        payload (ChatMessageRequest): The message content.
        db (Session): Database session dependency.

    Returns:
        ChatMessageResponse: Contains the AI's reply and a list of detected errors.

    Raises:
        HTTPException(404): If session not found.
        HTTPException(400): If session is not active or message is empty.
    """
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="Text is required")
    session = dao.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.status != models.SessionStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Session is not active")

    user_message = dao.append_message(db, session, models.MessageRole.USER, payload.text.strip())
    
    # Initialize LLM Client early for both tasks
    settings_row = dao.get_settings(db)
    llm_client = registry.get_llm(settings_row, config=runtime_config)

    detected_errors = error_service.detect_errors(payload.text, llm_client=llm_client)
    dao.save_error_spans(db, user_message, detected_errors)

    messages = dao.list_session_messages(db, session_id)
    system_prompt = session.system_prompt or _fallback_prompt()
    history = [{"role": "system", "content": system_prompt}]
    for msg in messages:
        history.append({"role": msg.role.value, "content": msg.text})

    reply = llm_client.reply(history)
    dao.append_message(db, session, models.MessageRole.ASSISTANT, reply)
    db.commit()

    return ChatMessageResponse(reply=reply, detected_errors=_serialize_errors(detected_errors))


@router.get("/{session_id}/history", response_model=list[ChatHistoryItem])
def get_session_history(session_id: str, db: Session = Depends(get_db)):
    session = dao.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    messages = dao.list_session_messages(db, session_id)
    return [
        ChatHistoryItem(role=msg.role.value, text=msg.text)
        for msg in messages
    ]
