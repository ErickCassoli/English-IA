from __future__ import annotations

from collections import Counter
from typing import Sequence

from app.repo.models import CEFRLevel, ErrorSpan, Message, MessageRole, QuizAttempt


def _is_user_message(message: Message) -> bool:
    if isinstance(message.role, MessageRole):
        return message.role == MessageRole.USER
    value = getattr(message.role, "value", message.role)
    return value == "user"


def _count_words(messages: Sequence[Message]) -> int:
    return sum(len(msg.text.split()) for msg in messages if msg.text and _is_user_message(msg))


def _accuracy(words: int, errors: int) -> float:
    if words <= 0:
        return 0.0
    return max(0.0, round((1 - (errors / words)) * 100, 2))


def _cefr_from_accuracy(value: float) -> CEFRLevel:
    if value >= 90:
        return CEFRLevel.C1
    if value >= 75:
        return CEFRLevel.B2
    if value >= 60:
        return CEFRLevel.B1
    return CEFRLevel.A2


def _quiz_summary(attempts: Sequence[QuizAttempt]) -> dict:
    if not attempts:
        return {"total": 0, "correct": 0, "accuracy_pct": 0.0}

    latest_attempts: dict[str, QuizAttempt] = {}
    for attempt in attempts:
        latest_attempts[attempt.quiz_id] = attempt

    total = len(latest_attempts)
    correct = sum(1 for attempt in latest_attempts.values() if attempt.is_correct)
    accuracy = round((correct / total) * 100, 2) if total else 0.0
    return {"total": total, "correct": correct, "accuracy_pct": accuracy}


def build_report(
    topic_label: str,
    messages: Sequence[Message],
    errors: Sequence[ErrorSpan],
    quiz_attempts: Sequence[QuizAttempt],
) -> dict:
    words = _count_words(messages)
    error_count = len(errors)
    accuracy = _accuracy(words, error_count)
    cefr = _cefr_from_accuracy(accuracy)
    category_counts = Counter(error.category.value for error in errors)
    quiz_data = _quiz_summary(quiz_attempts)

    strengths: list[str] = []
    improvements: list[str] = []
    if accuracy >= 80:
        strengths.append("High lexical accuracy across the session.")
    else:
        improvements.append("Focus on clarity by revising key corrections provided.")
    if category_counts.get("fluency"):
        improvements.append("Link short sentences to improve fluency.")
    if category_counts:
        for category, _ in category_counts.most_common(2):
            improvements.append(f"Revisit {category} patterns shown in corrections.")
    if not improvements:
        improvements.append("Keep expanding vocabulary with targeted drills.")

    examples = [
        {"source": error.user_text, "target": error.corrected_text, "note": error.note}
        for error in errors[:3]
    ]

    summary = (
        f"You practiced {topic_label.lower()} and produced {words} words with ~{accuracy}% accuracy "
        f"(CEFR {cefr.value}). You answered {quiz_data['correct']}/{quiz_data['total']} quiz items correctly."
    )

    return {
        "summary": summary,
        "kpis": {
            "words": words,
            "errors": error_count,
            "accuracy_pct": accuracy,
            "cefr_estimate": cefr.value,
        },
        "quiz_summary": quiz_data,
        "strengths": strengths or ["Consistent effort detected."],
        "improvements": improvements,
        "examples": examples,
    }
