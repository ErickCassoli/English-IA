from __future__ import annotations

from typing import List

from app.services.llm.base import HistoryMessage, LLMClient


class SimpleMockClient(LLMClient):
    """Deterministic offline model used for local dev and CI."""

    def reply(self, history: List[HistoryMessage]) -> str:
        last_user = next((msg["content"] for msg in reversed(history) if msg["role"] == "user"), "")
        if not last_user:
            return "Let's start practicing English!"
        return f"I noticed you said: \"{last_user}\". Here's a clearer version: {last_user.strip().capitalize()}."
