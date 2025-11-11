from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.repo import dao, models
from app.repo.db import get_db
from app.schemas.flashcard import (
    FlashcardReviewRequest,
    FlashcardReviewResponse,
    FlashcardSchema,
)
from app.services.evaluation import srs

router = APIRouter(prefix="/api/flashcards", tags=["flashcards"])


@router.get("/due", response_model=list[FlashcardSchema])
def due_flashcards(db: Session = Depends(get_db)):
    cards = dao.list_flashcards_due(db)
    return [
        FlashcardSchema(
            id=card.id,
            front=card.front,
            back=card.back,
            due_at=card.due_at,
            reps=card.reps,
            interval=card.interval,
            ease=float(card.ease),
        )
        for card in cards
    ]


@router.post("/{card_id}/review", response_model=FlashcardReviewResponse)
def review_flashcard(card_id: str, payload: FlashcardReviewRequest, db: Session = Depends(get_db)):
    card = db.get(models.Flashcard, card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    current_state = srs.CardState(reps=card.reps, interval=card.interval, ease=float(card.ease), due_at=card.due_at)
    next_state = srs.next_review(current_state, payload.quality)
    dao.update_flashcard_state(db, card, next_state.reps, next_state.interval, next_state.ease, next_state.due_at)
    db.commit()
    return FlashcardReviewResponse(id=card.id, due_at=card.due_at)
