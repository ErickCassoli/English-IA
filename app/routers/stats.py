from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.repo import dao
from app.utils import ids

router = APIRouter(prefix="/api/stats", tags=["stats"])


class StatsResponse(BaseModel):
    trace_id: str
    chats: int
    quizzes: int
    flashcards: int
    flashcards_due: int
    total_flashcards: int


@router.get("/summary", response_model=StatsResponse)
def get_summary() -> StatsResponse:
    trace_id = ids.new_trace_id()
    stats = dao.get_stats_summary()
    return StatsResponse(trace_id=trace_id, **stats)
