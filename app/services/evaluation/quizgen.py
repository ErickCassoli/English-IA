from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from typing import Iterable, Sequence

from app.repo.models import ErrorSpan, Message, MessageRole, QuizType

_STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "this",
    "that",
    "have",
    "from",
    "about",
    "your",
    "you",
    "just",
    "like",
    "they",
    "will",
    "them",
    "when",
    "what",
    "where",
    "which",
}
_CONTEXT_DISTRACTORS = [
    "beach",
    "museum",
    "mountain",
    "market",
    "station",
    "temple",
    "harbor",
]


@dataclass(slots=True)
class QuizPayload:
    type: QuizType
    prompt: str
    choices: list[str]
    answer: str
    source_error_id: str | None = None


def _is_user_message(message: Message) -> bool:
    role = getattr(message, "role", None)
    if role is None:
        return False
    if isinstance(role, MessageRole):
        return role == MessageRole.USER
    value = getattr(role, "value", role)
    return value == "user"


def _collect_user_text(messages: Iterable[Message]) -> str:
    return " ".join(msg.text for msg in messages if getattr(msg, "text", "") and _is_user_message(msg))


def _extract_keywords(messages: Sequence[Message]) -> list[str]:
    text = _collect_user_text(messages[-6:])
    tokens = re.findall(r"[A-Za-z][A-Za-z'\-]{3,}", text)
    if not tokens:
        return []
    counter = Counter()
    first_pos: dict[str, int] = {}
    title_case: dict[str, bool] = {}
    display: dict[str, str] = {}
    for idx, token in enumerate(tokens):
        lowered = token.lower()
        if lowered in _STOPWORDS:
            continue
        counter[lowered] += 1
        first_pos.setdefault(lowered, idx)
        display.setdefault(lowered, token)
        if token[0].isupper():
            title_case[lowered] = True
    items = list(counter.items())
    items.sort(key=lambda item: (-item[1], not title_case.get(item[0], False), first_pos.get(item[0], 0)))
    return [display[word] for word, _ in items[:3]]


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


def _context_choices(keyword: str) -> list[str]:
    choices = [keyword]
    for distractor in _CONTEXT_DISTRACTORS:
        if distractor.lower() == keyword.lower():
            continue
        choices.append(distractor.title())
        if len(choices) == 4:
            break
    return choices


def generate_quiz(topic: str, errors: Sequence[ErrorSpan], messages: Sequence[Message]) -> list[QuizPayload]:
    """Generate 3-5 deterministic quiz prompts referencing session errors and context."""
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

    keywords = _extract_keywords(messages)
    if keywords:
        keyword = keywords[0]
        prompt = f"Which place or detail did you mention while discussing {topic.lower()}?"
        items.append(
            QuizPayload(
                type=QuizType.MCQ,
                prompt=prompt,
                choices=_context_choices(keyword),
                answer=keyword.title(),
                source_error_id=None,
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
