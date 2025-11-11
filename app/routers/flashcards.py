from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/flashcards", tags=["flashcards"])


class Flashcard(BaseModel):
    id: str
    front: str
    back: str


class FlashcardReviewRequest(BaseModel):
    card_id: str
    quality: int


class FlashcardReviewResponse(BaseModel):
    card_id: str
    due_at: str


@router.get("/due", response_model=list[Flashcard])
async def list_due_cards() -> list[Flashcard]:
    return []


@router.post("/review", response_model=FlashcardReviewResponse)
async def review_card(_: FlashcardReviewRequest) -> FlashcardReviewResponse:
    return FlashcardReviewResponse(card_id="stub", due_at="1970-01-01T00:00:00Z")
