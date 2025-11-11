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
    due_at: datetime
    repetitions: int
    interval: int
    easiness: float


class FlashcardQueueResponse(BaseModel):
    trace_id: str
    flashcards: list[Flashcard]


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


@router.get("/due", response_model=FlashcardQueueResponse)
def get_due_flashcards(limit: int = 10) -> FlashcardQueueResponse:
    trace_id = ids.new_trace_id()
    cards = dao.get_flashcards_due(limit=limit)
    flashcards = [Flashcard(**card) for card in cards]
    return FlashcardQueueResponse(trace_id=trace_id, flashcards=flashcards)


@router.post("/review", response_model=FlashcardReviewResponse)
def review_flashcard(payload: FlashcardReviewRequest) -> FlashcardReviewResponse:
    trace_id = ids.new_trace_id()
    card = dao.get_flashcard(payload.card_id)
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Flashcard not found")
    state = srs.CardState(
        repetitions=card["repetitions"],
        interval=card["interval"],
        easiness=card["easiness"],
        due_at=datetime.fromisoformat(card["due_at"]),
    )
    updated = srs.review_card(state, payload.quality)
    dao.update_flashcard_state(
        card_id=payload.card_id,
        repetitions=updated.repetitions,
        interval=updated.interval,
        easiness=updated.easiness,
        due_at=updated.due_at,
    )
    return FlashcardReviewResponse(
        trace_id=trace_id,
        card_id=payload.card_id,
        due_at=updated.due_at,
        repetitions=updated.repetitions,
        interval=updated.interval,
        easiness=updated.easiness,
    )
