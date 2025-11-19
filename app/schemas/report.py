from __future__ import annotations

from pydantic import BaseModel


class ReportResponse(BaseModel):
    words: int
    errors: int
    accuracy_pct: float
    cefr: str
    strengths: list[str]
    improvements: list[str]
    examples: list[dict[str, str]]
