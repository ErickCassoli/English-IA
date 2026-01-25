from types import SimpleNamespace

from app.services.evaluation import report


def _msg(text: str) -> SimpleNamespace:
    return SimpleNamespace(text=text, role=SimpleNamespace(value="user"))


def _error() -> SimpleNamespace:
    return SimpleNamespace(
        category=SimpleNamespace(value="grammar"),
        user_text="I am agree",
        corrected_text="I agree",
        note="Use agree without am.",
    )


def test_report_includes_quiz_summary():
    messages = [_msg("I loved visiting Paris last summer.")]
    errors = [_error()]
    quiz_attempts = [
        SimpleNamespace(quiz_id="q1", is_correct=True),
        SimpleNamespace(quiz_id="q2", is_correct=False),
    ]
    data = report.build_report("travel", messages, errors, quiz_attempts)
    assert data["quiz_summary"]["total"] == 2
    assert data["quiz_summary"]["correct"] == 1
    assert "2" in data["summary"]
