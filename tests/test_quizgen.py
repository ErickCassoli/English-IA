from types import SimpleNamespace

from app.services.evaluation.quizgen import generate_quiz


def test_generate_quiz_includes_error_and_topic():
    errors = [
        SimpleNamespace(id="err-1", user_text="I am agree", corrected_text="I agree"),
        SimpleNamespace(id="err-2", user_text="peoples", corrected_text="people"),
    ]
    items = generate_quiz("travel", errors)
    assert 3 <= len(items) <= 5
    assert any(item.source_error_id == "err-1" for item in items)
    assert any("travel" in item.prompt.lower() for item in items)
