from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/stats", tags=["stats"])


class StatsResponse(BaseModel):
    last_7_days_minutes: int = 0
    accuracy_estimate: float = 0.0
    top_error_tags: list[str] = []


@router.get("/summary", response_model=StatsResponse)
async def get_summary() -> StatsResponse:
    return StatsResponse()
