from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.repo import dao
from app.services import srs
from app.utils import ids

router = APIRouter(prefix="/api/flashcards", tags=["flashcards"])


class Flashcard(BaseModel):
    id: str
    front: str
    back: str
    tag: str | None = None
    repetitions: int
    interval: int
    easiness: float
    due_at: datetime


class FlashcardReviewRequest(BaseModel):
    card_id: str
    quality: int = Field(ge=0, le=5)


class FlashcardReviewResponse(BaseModel):
    trace_id: str
    card_id: str
    due_at: datetime
    repetitions: int
    interval: int
    easiness: float


@router.get("/due", response_model=list[Flashcard])
def list_due_cards(limit: int = 10) -> list[Flashcard]:
    cards = dao.get_flashcards_due(limit=limit)
    return [Flashcard(**card) for card in cards]


@router.post("/review", response_model=FlashcardReviewResponse)
def review_card(payload: FlashcardReviewRequest) -> FlashcardReviewResponse:
    trace_id = ids.new_trace_id()
    cards = {card["id"]: card for card in dao.get_flashcards_due(limit=100)}
    card = cards.get(payload.card_id)
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flashcard not due or missing",
        )
    state = srs.CardState(
        repetitions=card["repetitions"],
        interval=card["interval"],
        easiness=card["easiness"],
        due_at=datetime.fromisoformat(card["due_at"]),
    )
    updated = srs.review(state, payload.quality)
    dao.update_flashcard_state(
        card_id=payload.card_id,
        repetitions=updated.repetitions,
        interval=updated.interval,
        easiness=updated.easiness,
        due_at=updated.due_at,
    )
    dao.bump_daily_stats(minutes=2, accuracy=0.9, error_tag="flashcards")
    return FlashcardReviewResponse(
        trace_id=trace_id,
        card_id=payload.card_id,
        due_at=updated.due_at,
        repetitions=updated.repetitions,
        interval=updated.interval,
        easiness=updated.easiness,
    )
