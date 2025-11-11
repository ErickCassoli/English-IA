from __future__ import annotations

import httpx

from app.services.llm.base import HistoryMessage, LLMClient


class OpenAIClient(LLMClient):
    def __init__(self, api_key: str, model: str):
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required for the openai provider")
        self.api_key = api_key
        self.model = model

    def reply(self, history: list[HistoryMessage]) -> str:
        payload = {"model": self.model, "messages": history, "temperature": 0.2}
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            response = httpx.post(
                "https://api.openai.com/v1/chat/completions",
                json=payload,
                headers=headers,
                timeout=15.0,
            )
            response.raise_for_status()
            data = response.json()
            message = data["choices"][0]["message"]["content"]
            return message.strip()
        except Exception as exc:  # pragma: no cover - network dependent
            return f"(offline) Unable to reach OpenAI: {exc}. Let's review your sentence again."
