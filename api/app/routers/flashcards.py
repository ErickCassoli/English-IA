from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.repo import dao, models
from app.repo.db import get_db
from app.schemas.flashcard import (
    FlashcardManualCreateRequest,
    FlashcardReviewRequest,
    FlashcardReviewResponse,
    FlashcardSchema,
)
from app.services.evaluation import srs

"""
Flashcards Router
=================

Manages the Spaced Repetition System (SRS) for vocabulary retention.
The core logic relies on `app.services.evaluation.srs` (modified SM-2 algorithm).

Endpoints:
    - GET /: List all cards.
    - GET /due: List cards scheduled for review NOW.
    - POST /{id}/review: Submit a review grade (0-5) to reschedule the card.
    - POST /manual: Manually create a card.
"""

router = APIRouter(prefix="/api/flashcards", tags=["flashcards"])


@router.get("", response_model=list[FlashcardSchema])
def list_flashcards(db: Session = Depends(get_db)):
    cards = dao.list_all_flashcards(db)
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


@router.delete("/{card_id}", status_code=204)
def delete_flashcard(card_id: str, db: Session = Depends(get_db)):
    success = dao.delete_flashcard(db, card_id)
    if not success:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    db.commit()


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
    """
    Process a review limit for a flashcard using SRS.

    Algorithm:
    1. Retrieve current card state (Ease Factor, Interval, Reps).
    2. Apply modified SM-2 algorithm based on user quality rating (0-5).
    3. Calculate the NEXT due date.
    4. Update DB.

    Args:
        card_id (str): UUID.
        payload (FlashcardReviewRequest): Quality score (0=Blackout, 5=Perfect).

    Returns:
        FlashcardReviewResponse: New due date.
    """
    card = db.get(models.Flashcard, card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    current_state = srs.CardState(reps=card.reps, interval=card.interval, ease=float(card.ease), due_at=card.due_at)
    next_state = srs.next_review(current_state, payload.quality)
    dao.update_flashcard_state(db, card, next_state.reps, next_state.interval, next_state.ease, next_state.due_at)
    db.commit()
    return FlashcardReviewResponse(id=card.id, due_at=card.due_at)


@router.post("/manual", response_model=FlashcardSchema, status_code=201)
def create_manual_flashcard(payload: FlashcardManualCreateRequest, db: Session = Depends(get_db)):
    front = payload.front.strip()
    back = payload.back.strip()
    if not front or not back:
        raise HTTPException(status_code=400, detail="front and back are required")
    card = dao.create_manual_flashcard(db, front, back)
    db.commit()
    return FlashcardSchema(
        id=card.id,
        front=card.front,
        back=card.back,
        due_at=card.due_at,
        reps=card.reps,
        interval=card.interval,
        ease=float(card.ease),
    )
