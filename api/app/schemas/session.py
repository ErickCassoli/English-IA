from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SessionCreateRequest(BaseModel):
    topic_code: Optional[str] = Field(
        default=None, description="Optional practice topic code; random when omitted."
    )
    custom_topic: Optional[str] = Field(
        default=None, description="Custom free-text topic if code is not provided."
    )


class SessionResponse(BaseModel):
    session_id: str
    topic_code: str
    topic_label: str
    topic_description: str
    system_prompt: str
    status: str
    started_at: datetime
    ended_at: Optional[datetime]
    active_minutes: float = Field(default=0.0)
    last_interaction_at: Optional[datetime]


class QuizItemSchema(BaseModel):
    id: str
    type: str
    prompt: str
    choices_json: str
    answer: str

class SessionFinishResponse(BaseModel):
    quizzes_created: int
    flashcards_created: int
    report_ready: bool = False
    quizzes: Optional[list[QuizItemSchema]] = None
