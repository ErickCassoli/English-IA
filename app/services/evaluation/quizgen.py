from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from app.repo.models import ErrorSpan, QuizType


@dataclass(slots=True)
class QuizPayload:
    type: QuizType
    prompt: str
    choices: list[str]
    answer: str
    source_error_id: str | None = None


def _build_choices(correct: str, wrong: str) -> list[str]:
    pool = [
        correct,
        wrong,
        correct.lower(),
        f"{wrong}?",
    ]
    seen: set[str] = set()
    deduped: list[str] = []
    for choice in pool:
        normalized = choice.strip()
        if not normalized or normalized in seen:
            continue
        deduped.append(normalized)
        seen.add(normalized)
        if len(deduped) == 4:
            break
    if len(deduped) < 2:
        deduped.append("I don't know")
    return deduped


def generate_quiz(topic: str, errors: Sequence[ErrorSpan]) -> list[QuizPayload]:
    """Generate 3-5 deterministic quiz prompts prioritizing session errors."""
    items: list[QuizPayload] = []

    for error in list(errors)[:4]:
        correct = error.corrected_text.strip()
        wrong = error.user_text.strip()
        prompt = f"Choose the best correction for \"{wrong}\""
        choices = _build_choices(correct, wrong)
        items.append(
            QuizPayload(
                type=QuizType.MCQ,
                prompt=prompt,
                choices=choices,
                answer=correct,
                source_error_id=error.id,
            )
        )

    if len(items) < 3:
        baseline_prompt = f"What is a synonym for the topic '{topic}'?"
        items.append(
            QuizPayload(
                type=QuizType.CLOZE,
                prompt=baseline_prompt,
                choices=[topic, f"{topic} practice", "grammar"],
                answer=topic,
                source_error_id=None,
            )
        )

    comprehension_prompt = f"What was the main theme of your session? ({topic})"
    items.append(
        QuizPayload(
            type=QuizType.MCQ,
            prompt=comprehension_prompt,
            choices=[topic, "small talk", "travel"],
            answer=topic,
            source_error_id=None,
        )
    )

    # Ensure 3-5 items deterministically
    unique_items: list[QuizPayload] = []
    seen_prompts: set[str] = set()
    for item in items:
        if item.prompt in seen_prompts:
            continue
        unique_items.append(item)
        seen_prompts.add(item.prompt)
        if len(unique_items) == 5:
            break

    while len(unique_items) < 3:
        filler_prompt = f"Complete the idea about '{topic}'"
        unique_items.append(
            QuizPayload(
                type=QuizType.CLOZE,
                prompt=filler_prompt,
                choices=[f"{topic} is important", f"I enjoy {topic}", "Practice helps"],
                answer=f"I enjoy {topic}",
                source_error_id=None,
            )
        )

    return unique_items
