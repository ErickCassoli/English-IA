from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.repo.db import get_db

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.delete("/reset", status_code=status.HTTP_204_NO_CONTENT)
def reset_data(db: Session = Depends(get_db)):
    """
    DANGER: Wipes all user data including sessions, messages, quizzes,
    flashcards, daily practices, and metric snapshots.
    Keeps Settings and configured PracticeTopics.
    """
    # Order matters due to foreign keys
    tables = [
        "daily_practices",
        "user_streaks",
        "quiz_attempts",
        "quizzes",
        "flashcards",
        "error_spans",
        "messages",
        "metric_snapshots",
        "sessions",
        "users",
    ]
    
    try:
        # Disable foreign key checks for SQLite to allow clean truncation if needed, 
        # though deleting in order is safer.
        # SQLite doesn't have TRUNCATE, so using DELETE
        for table in tables:
            db.execute(text(f"DELETE FROM {table}"))
        
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Failed to reset data: {str(e)}"
        ) from e
