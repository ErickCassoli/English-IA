from __future__ import annotations

from pydantic import BaseModel


class DashboardSummary(BaseModel):
    study_time_hours: float
    words_learned: int
    conversations: int
    fluency_level: str
    due_flashcards: int
