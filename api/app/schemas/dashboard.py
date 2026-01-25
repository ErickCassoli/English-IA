from __future__ import annotations

from datetime import date

from pydantic import BaseModel


class DashboardSummary(BaseModel):
    study_time_hours: float
    study_time_total_seconds: float
    words_learned: int
    conversations: int
    fluency_level: str
    fluency_score: float # 0.0 to 100.0 or similar
    is_assessed: bool
    skills: dict[str, float] # { "reading": 0.0, "writing": 0.0, "listening": 0.0, "speaking": 0.0 }
    due_flashcards: int
    minutes_today: float
    current_streak_days: int
    longest_streak_days: int
    last_practice_date: date | None
