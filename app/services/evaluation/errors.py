from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List

from app.repo.models import ErrorCategory


@dataclass(slots=True)
class DetectedError:
    start: int
    end: int
    category: ErrorCategory
    user_text: str
    corrected_text: str
    note: str


_PATTERNS = [
    ("i am agree", "I agree", ErrorCategory.GRAMMAR, "Use 'agree' without the auxiliary verb."),
    ("peoples", "people", ErrorCategory.VOCAB, "The plural of person is 'people'."),
    ("more better", "better", ErrorCategory.GRAMMAR, "Comparatives do not take 'more'."),
]


def _find_pattern_errors(text: str) -> List[DetectedError]:
    lowered = text.lower()
    errors: List[DetectedError] = []
    for pattern, correction, category, note in _PATTERNS:
        start = 0
        while True:
            idx = lowered.find(pattern, start)
            if idx == -1:
                break
            end = idx + len(pattern)
            errors.append(
                DetectedError(
                    start=idx,
                    end=end,
                    category=category,
                    user_text=text[idx:end],
                    corrected_text=correction,
                    note=note,
                )
            )
            start = end
    year_match = re.search(r"\bi have (\d{1,2}) years\b", lowered)
    if year_match:
        idx = year_match.start()
        age = year_match.group(1)
        end = year_match.end()
        errors.append(
            DetectedError(
                start=idx,
                end=end,
                category=ErrorCategory.GRAMMAR,
                user_text=text[idx:end],
                corrected_text=f"I am {age} years old",
                note="Use the verb 'to be' to express age.",
            )
        )
    return errors


def _detect_fluency(text: str) -> List[DetectedError]:
    sentences = [fragment.strip() for fragment in re.split(r"[.!?]", text) if fragment.strip()]
    short_sentences = [s for s in sentences if len(s.split()) <= 3]
    if len(short_sentences) < 2:
        return []
    fragment = short_sentences[0]
    start = text.find(fragment)
    end = start + len(fragment)
    return [
        DetectedError(
            start=start,
            end=end,
            category=ErrorCategory.FLUENCY,
            user_text=fragment,
            corrected_text="Combine short sentences for smoother speech.",
            note="Multiple short utterances detected; try linking ideas.",
        )
    ]


def detect_errors(text: str) -> List[DetectedError]:
    """Return heuristic error spans for the provided sentence."""
    errors = _find_pattern_errors(text)
    errors.extend(_detect_fluency(text))
    return errors
