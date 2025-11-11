from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    id: str
    trace_id: str
    user_input: str
    corrected: str
    metadata: dict[str, str] | None = None
    created_at: datetime


class QuizQuestion(BaseModel):
    id: str
    prompt: str
    options: list[str] = Field(default_factory=list)
    answer: str
    rationale: str


class Flashcard(BaseModel):
    id: str
    front: str
    back: str
    tag: str | None = None
    repetitions: int
    interval: int
    easiness: float
    due_at: datetime


class StatsSummary(BaseModel):
    last_7_days_minutes: int
    accuracy_estimate: float
    top_error_tags: list[str]
