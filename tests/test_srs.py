from __future__ import annotations

from datetime import UTC, datetime

from app.services import srs


def test_sm2_progression_and_lapse():
    state = srs.CardState(repetitions=0, interval=0, easiness=2.5, due_at=datetime.now(tz=UTC))
    first = srs.review(state, 5)
    assert first.repetitions == 1
    assert first.interval == 1
    second = srs.review(first, 4)
    assert second.repetitions == 2
    assert second.interval >= 1
    lapse = srs.review(second, 1)
    assert lapse.repetitions == 0
    assert lapse.interval == 1
