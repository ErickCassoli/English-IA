from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SessionCreateRequest(BaseModel):
    topic_code: Optional[str] = Field(
        default=None, description="Optional practice topic code; random when omitted."
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


class SessionFinishResponse(BaseModel):
    quizzes_created: int
    flashcards_created: int
    report_ready: bool = False
