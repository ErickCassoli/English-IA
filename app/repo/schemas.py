from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class ChatMessage:
    id: str
    trace_id: str
    user_input: str
    corrected: str
    metadata: dict[str, Any]
    created_at: datetime


@dataclass
class QuizQuestion:
    id: str
    prompt: str
    options: list[str]
    answer: str
    rationale: str


@dataclass
class FlashcardRow:
    id: str
    front: str
    back: str
    tag: str | None
    repetitions: int
    interval: int
    easiness: float
    due_at: datetime
