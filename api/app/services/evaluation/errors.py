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


from pathlib import Path
import json
from app.repo import dao
from app.repo.db import get_db
from app.services.llm import registry
from app.utils.config import get_settings

def _detect_with_llm(text: str) -> List[DetectedError]:
    try:
        settings = get_settings()
        # We need a db session to get settings for LLM key, but usually this service is called within a request.
        # Ideally, we pass llm_client in. For now, let's try to get a temporary session or use default config if possible.
        # But wait, `registry.get_llm` needs `settings_row`.
        # Simplification: Assume environment variables for keys if DB access is complex here.
        # OR: Refactor `detect_errors` signature to accept `llm_client`.
        # However, `chat.py` calls `detect_errors` and it HAS a db session.
        # Correct approach: Update `detect_errors` signature to accept `db`.
        pass 
    except Exception:
        return []

# We will change the signature of `detect_errors` in checking `chat.py` next.
# For now, let's implement the logic assuming we have an LLM client or can get one.

def detect_errors(text: str, llm_client=None) -> List[DetectedError]:
    """Return error spans for the provided sentence using LLM if available, else regex."""
    if not text or len(text.strip()) < 3:
        return []

    # Heuristics first (fast)
    heuristic_errors = _find_pattern_errors(text)
    heuristic_errors.extend(_detect_fluency(text))
    
    if not llm_client:
        return heuristic_errors

    # LLM Detection
    try:
        prompt_path = Path(__file__).resolve().parents[3] / "prompts" / "correction.poml"
        if not prompt_path.exists():
            return heuristic_errors

        # Minimal prompt construction (if not using full POML parser)
        # Or load the content.
        content = prompt_path.read_text(encoding="utf-8")
        
        # Simple string replacement for now
        prompt = f"""You are an English coach.
Correct the learner message. Return specific error spans.
Learner message: "{text}"
Return strictly JSON format:
{{
  "rectified": "Full corrected sentence",
  "errors": [
    {{"start": 0, "end": 5, "category": "grammar", "correction": "I am", "note": "Use 'I am' instead of 'I have' for age/state."}}
  ]
}}
If no errors, return {{"rectified": "{text}", "errors": []}}
"""
        response_text = llm_client.reply([{"role": "user", "content": prompt}])
        
        # Parse JSON
        start_json = response_text.find("{")
        end_json = response_text.rfind("}") + 1
        if start_json == -1 or end_json == 0:
            return heuristic_errors
            
        data = json.loads(response_text[start_json:end_json])
        
        llm_errors = []
        for e in data.get("errors", []):
            # Validate indices
            s, end_ = e.get("start"), e.get("end")
            if s is not None and end_ is not None:
                # Ensure within bounds
                s = max(0, int(s))
                end_ = min(len(text), int(end_))
                
                cat_str = e.get("category", "grammar").upper()
                try:
                    cat = ErrorCategory(cat_str)
                except:
                    cat = ErrorCategory.GRAMMAR
                    
                llm_errors.append(DetectedError(
                    start=s,
                    end=end_,
                    category=cat,
                    user_text=text[s:end_],
                    corrected_text=e.get("correction", "Fixed"),
                    note=e.get("note", "Correction needed")
                ))
                
        return llm_errors if llm_errors else heuristic_errors

    except Exception as e:
        print(f"[ERROR] LLM Correction failed: {e}")
        return heuristic_errors
