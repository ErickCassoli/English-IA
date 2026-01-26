from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
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
        # Common confusion patterns (heuristic)
        correct.replace("in", "on").replace("at", "in") if "in" in correct or "at" in correct else "",
        f"not {correct}",
        wrong.capitalize() if wrong[0].islower() else wrong.lower(),
    ]
    
    seen: set[str] = {correct, wrong}
    deduped: list[str] = [correct, wrong]
    
    # Filter and fill
    for choice in pool:
        normalized = choice.strip()
        if not normalized or normalized.lower() == correct.lower() or normalized.lower() == wrong.lower():
            continue
        if normalized in seen:
            continue
            
        deduped.append(normalized)
        seen.add(normalized)
        if len(deduped) >= 4:
            break
            
    # Fallbacks if we still don't have enough options
    if len(deduped) < 4:
        fallbacks = ["I don't know", f"{correct}?", "None of the above"]
        for fb in fallbacks:
            if fb not in seen:
                deduped.append(fb)
                seen.add(fb)
            if len(deduped) >= 4:
                break
                
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
        
        # Filter out bad candidates
        if len(wrong) < 3 and wrong.lower() not in ["i", "a", "an", "to", "in", "on", "at"]:
            continue
        if len(correct) > len(wrong) * 3 and len(wrong) < 5:
            # Avoid "h" -> "I am very sorry..."
            continue
            
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


@dataclass
class FlashcardPayload:
    front: str
    back: str
    source_error_id: str | None = None


from app.utils.prompts import poml

def _load_prompt_template(transcript: str) -> str:
    path = Path(__file__).resolve().parents[3] / "prompts" / "session_analysis.poml"
    try:
        return poml.load(path, variables={"transcript": transcript})
    except Exception as e:
        print(f"POML Load Error: {e}")
        return f"Analyze this transcript: {transcript}"


def generate_quiz_with_llm(
    llm,
    topic: str,
    errors: Sequence[ErrorSpan],
    messages: Sequence[Message]
) -> tuple[list[QuizPayload], list[FlashcardPayload]]:
    """Generate quizzes and flashcards using LLM analysis of the session."""
    
    # 1. Build transcript
    transcript_lines = []
    for msg in messages:
        role_label = "Learner" if msg.role == MessageRole.USER else "Tutor"
        transcript_lines.append(f"{role_label}: {msg.text}")
    
    transcript_text = "\n".join(transcript_lines)
    
    # 2. Load and format prompt
    prompt_text = _load_prompt_template(transcript_text)
    
    # 3. Call LLM
    history = [{"role": "user", "content": prompt_text}]
    response_text = llm.reply(history)
    
    # DEBUG: Log the response
    print(f"[DEBUG] LLM Response length: {len(response_text)}")
    print(f"[DEBUG] LLM Response preview: {response_text[:500]}...")
    
    # 4. Extract JSON from response (handle markdown code blocks)
    clean_text = response_text.strip()
    if "```json" in clean_text:
        clean_text = clean_text.split("```json")[1].split("```")[0].strip()
    elif "```" in clean_text:
        # Try to find JSON between any code blocks
        parts = clean_text.split("```")
        for part in parts:
            if "{" in part and "}" in part:
                clean_text = part.strip()
                break
    
    # 5. Parse JSON
    data = {"quizzes": [], "flashcards": []}
    try:
        data = json.loads(clean_text)
    except json.JSONDecodeError as e:
        print(f"Failed to decode quiz JSON: {e}")
        print(f"Response was: {clean_text[:200]}...")
        # Return empty if parsing fails
        return [], []

    # 6. Convert to payloads
    quiz_payloads = []
    flashcard_payloads = []

    for q in data.get("quizzes", []):
        try:
            quiz_payloads.append(QuizPayload(
                type=QuizType.MCQ,
                prompt=q["prompt"],
                choices=q["choices"],
                answer=q["answer"],
                source_error_id=None
            ))
        except (KeyError, TypeError) as e:
            print(f"Skipping malformed quiz: {e}")
            continue

    for f in data.get("flashcards", []):
        try:
            flashcard_payloads.append(FlashcardPayload(
                front=f["front"],
                back=f["back"],
                source_error_id=None
            ))
        except (KeyError, TypeError) as e:
            print(f"Skipping malformed flashcard: {e}")
            continue
            
    return quiz_payloads, flashcard_payloads
