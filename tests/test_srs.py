from datetime import UTC, datetime

from app.services.srs import CardState, review_card


def test_sm2_progression_and_lapse():
    start = CardState(repetitions=0, interval=0, easiness=2.5, due_at=datetime.now(tz=UTC))
    first = review_card(start, quality=5)
    assert first.repetitions == 1
    assert first.interval == 1

    second = review_card(first, quality=4)
    assert second.repetitions == 2
    assert second.interval >= first.interval

    lapse = review_card(second, quality=2)
    assert lapse.repetitions == 0
    assert lapse.interval == 1
