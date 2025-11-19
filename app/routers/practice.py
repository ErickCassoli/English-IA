from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.repo import dao
from app.repo.db import get_db
from app.schemas.practice import PracticeTopicSchema

router = APIRouter(prefix="/api/practice", tags=["practice"])


@router.get("/topics", response_model=list[PracticeTopicSchema])
def list_topics(db: Session = Depends(get_db)) -> list[PracticeTopicSchema]:
    topics = dao.list_practice_topics(db)
    return [
        PracticeTopicSchema(code=topic.code, label=topic.label, description=topic.description)
        for topic in topics
    ]
