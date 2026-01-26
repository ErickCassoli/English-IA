from __future__ import annotations

import json
from pathlib import Path

from app.repo import models
from app.services.llm import registry


def _load_prompt() -> str:
    path = Path(__file__).resolve().parents[3] / "prompts" / "placement_assessment.poml"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return "Analyze the following conversation and return JSON with keys: cefr_level, score_0_100, justification."


def evaluate_session(
    llm_client: registry.LLMClient,
    messages: list[models.Message]
) -> dict:
    conversation_text = ""
    for msg in messages:
        role = "Examiner" if msg.role == models.MessageRole.ASSISTANT else "Candidate"
        conversation_text += f"{role}: {msg.text}\n"

    from app.utils.prompts import poml
    path = Path(__file__).resolve().parents[3] / "prompts" / "placement_assessment.poml"
    
    try:
        prompt = poml.load(path, variables={"transcript": conversation_text})
    except Exception as e:
        print(f"POML Load Error: {e}")
        # Fallback
        prompt = f"Analyze the following conversation: {conversation_text}. Return JSON {{'cefr_level': 'A1', ...}}"
    
    # We ask the LLM for a JSON response
    response_text = llm_client.reply([{"role": "user", "content": prompt}])
    
    # Simple parsing (robustness improvements could be added)
    try:
        # Strip code blocks if present
        cleaned = response_text.replace("```json", "").replace("```", "").strip()
        data = json.loads(cleaned)
        return data
    except Exception:
        # Fallback if JSON fails
        print(f"[WARN] Failed to parse placement JSON. Response: {response_text}")
        return {
            "cefr_level": "A1",
            "score_0_100": 10,
            "justification": "Could not parse assessment result. Defaulting to A1."
        }
