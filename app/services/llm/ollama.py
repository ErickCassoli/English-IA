from __future__ import annotations

import httpx

from app.services.llm.base import HistoryMessage, LLMClient


class OllamaClient(LLMClient):
    def __init__(self, base_url: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def reply(self, history: list[HistoryMessage]) -> str:
        prompt = "\n".join(f"{msg['role']}: {msg['content']}" for msg in history)
        payload = {"model": self.model, "prompt": prompt, "stream": False}
        try:
            response = httpx.post(f"{self.base_url}/api/generate", json=payload, timeout=15.0)
            response.raise_for_status()
            data = response.json()
            return data.get("response") or data.get("output") or "Let's keep practicing!"
        except Exception as exc:  # pragma: no cover - network dependent
            return f"(offline) Unable to reach Ollama: {exc}. Let's keep practicing!"
