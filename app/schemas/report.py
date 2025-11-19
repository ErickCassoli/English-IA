from __future__ import annotations

from pydantic import BaseModel


class ReportKPIs(BaseModel):
    words: int
    errors: int
    accuracy_pct: float
    cefr_estimate: str


class ReportExample(BaseModel):
    source: str
    target: str
    note: str


class ReportResponse(BaseModel):
    summary: str
    kpis: ReportKPIs
    strengths: list[str]
    improvements: list[str]
    examples: list[ReportExample]
