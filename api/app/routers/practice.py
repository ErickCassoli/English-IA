from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.repo import dao
from app.repo.db import get_db
from app.schemas.practice import PracticeTopicSchema

router = APIRouter(prefix="/api/practice", tags=["practice"])


@router.get("/topics", response_model=list[PracticeTopicSchema])
def list_topics(db: Session = Depends(get_db)) -> list[PracticeTopicSchema]:
    # Filter out custom user topics (they start with 'custom_') or legacy 'custom'
    topics = [t for t in topics if not t.code.startswith("custom_") and t.code != "custom"]
    return [
        PracticeTopicSchema(code=topic.code, label=topic.label, description=topic.description)
        for topic in topics
    ]
