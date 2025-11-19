from datetime import UTC, datetime

from app.services.evaluation import srs


def test_srs_progression_improves_reps():
    now = datetime.now(tz=UTC)
    state = srs.CardState(reps=0, interval=0, ease=2.5, due_at=now)
    next_state = srs.next_review(state, quality=4)
    assert next_state.reps == 1
    assert next_state.interval == 1
    later_state = srs.next_review(next_state, quality=5)
    assert later_state.reps == 2
    assert later_state.interval >= 6
