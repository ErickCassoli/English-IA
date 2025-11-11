from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta


@dataclass(slots=True)
class CardState:
    reps: int
    interval: int
    ease: float
    due_at: datetime


def next_review(state: CardState, quality: int) -> CardState:
    quality = max(0, min(5, quality))
    ease = state.ease + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    ease = max(1.3, ease)
    if quality < 3:
        reps = 0
        interval = 1
    else:
        reps = state.reps + 1
        if reps == 1:
            interval = 1
        elif reps == 2:
            interval = 6
        else:
            interval = int(round(state.interval * ease)) or 1
    due_at = datetime.now(tz=UTC) + timedelta(days=interval)
    return CardState(reps=reps, interval=interval, ease=ease, due_at=due_at)
