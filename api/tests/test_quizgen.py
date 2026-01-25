from types import SimpleNamespace

from app.services.evaluation.quizgen import generate_quiz


def _message(text: str) -> SimpleNamespace:
    return SimpleNamespace(text=text, role=SimpleNamespace(value="user"))


def test_generate_quiz_includes_error_and_topic():
    errors = [
        SimpleNamespace(id="err-1", user_text="I am agree", corrected_text="I agree"),
        SimpleNamespace(id="err-2", user_text="peoples", corrected_text="people"),
    ]
    messages = [_message("I am agree with peoples"), _message("Let's talk about travel.")]
    items = generate_quiz("travel", errors, messages)
    assert 3 <= len(items) <= 5
    assert any(item.source_error_id == "err-1" for item in items)
    assert any("travel" in item.prompt.lower() for item in items)


def test_generate_quiz_references_conversation_context():
    errors: list[SimpleNamespace] = []
    messages = [_message("I loved visiting Paris and Rome during my trip.")]
    items = generate_quiz("travel", errors, messages)
    assert any("paris" in choice.lower() for item in items for choice in item.choices)
