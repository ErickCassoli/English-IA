from __future__ import annotations

from pydantic import BaseModel, Field


class QuizItemSchema(BaseModel):
    id: str
    type: str
    prompt: str
    choices: list[str]


class QuizListResponse(BaseModel):
    items: list[QuizItemSchema]


class QuizAnswerRequest(BaseModel):
    choice: str
    latency_ms: int = Field(ge=0, default=0)


class QuizAnswerResponse(BaseModel):
    quiz_id: str
    is_correct: bool
    flashcard_created: bool
    report_ready: bool
