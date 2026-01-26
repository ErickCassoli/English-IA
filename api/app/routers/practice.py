from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.repo import dao
from app.repo.db import get_db
from app.schemas.practice import PracticeTopicSchema

"""
Practice Router
===============

Manages static and dynamic practice topics.
"""

router = APIRouter(prefix="/api/practice", tags=["practice"])


@router.get("/topics", response_model=list[PracticeTopicSchema])
def list_topics(db: Session = Depends(get_db)) -> list[PracticeTopicSchema]:
    """
    Retrieve all available conversation topics.

    Filters out:
    - Custom ad-hoc topics created by users (starts with 'custom_').
    - 'placement' topics (handled separately by frontend logic).

    Returns:
        list[PracticeTopicSchema]: Clean list of curated topics (Travel, Gaming, etc.).
    """
    # Filter out custom user topics (they start with 'custom_') or legacy 'custom'
    all_topics = dao.list_practice_topics(db)
    # Filter out custom user topics (they start with 'custom_') or legacy 'custom'
    # Also filter placement tests if desired, but frontend handles them. keeping them for now to allow locking logic.
    filtered = [
        t for t in all_topics 
        if not t.code.startswith("custom_") 
        and t.code != "custom" 
        and "placement" not in t.code
    ]
    return [
        PracticeTopicSchema(code=topic.code, label=topic.label, description=topic.description)
        for topic in filtered
    ]
