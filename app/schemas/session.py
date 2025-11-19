from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SessionCreateRequest(BaseModel):
    topic: Optional[str] = Field(default=None, description="Optional conversation topic.")


class SessionResponse(BaseModel):
    id: str
    topic: str
    status: str
    started_at: datetime
    ended_at: Optional[datetime]


class SessionFinishResponse(BaseModel):
    quizzes_created: int
    flashcards_created: int
    report_ready: bool = True
