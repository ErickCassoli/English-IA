from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class FlashcardSchema(BaseModel):
    id: str
    front: str
    back: str
    due_at: datetime
    reps: int
    interval: int
    ease: float


class FlashcardReviewRequest(BaseModel):
    quality: int = Field(ge=0, le=5)


class FlashcardReviewResponse(BaseModel):
    id: str
    due_at: datetime
