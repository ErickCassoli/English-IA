from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta


@dataclass
class CardState:
    repetitions: int
    interval: int
    easiness: float
    due_at: datetime


def review_card(state: CardState, quality: int) -> CardState:
    """SM-2 spaced repetition algorithm."""
    quality = max(0, min(5, quality))
    easiness = state.easiness + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    easiness = max(1.3, easiness)

    if quality < 3:
        repetitions = 0
        interval = 1
    else:
        repetitions = state.repetitions + 1
        if repetitions == 1:
            interval = 1
        elif repetitions == 2:
            interval = 6
        else:
            interval = round(state.interval * easiness)

    due_at = datetime.now(tz=UTC) + timedelta(days=interval)
    return CardState(repetitions=repetitions, interval=interval, easiness=easiness, due_at=due_at)
