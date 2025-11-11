from __future__ import annotations

import json
from typing import Any

import httpx

from app.utils.logger import get_logger

log = get_logger(__name__)


async def generate_prompt(prompt: str, *, trace_id: str, settings, fallback: Any) -> str:
    """Call Ollama (or similar) and fall back to deterministic JSON."""
    url = settings.ollama_host.rstrip("/") + "/api/generate"
    payload = {"model": settings.llm_model, "prompt": prompt, "stream": False}
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            text = (data.get("response") or data.get("output") or "").strip()
            if not text:
                raise ValueError("LLM returned an empty response")
            return text
    except Exception as exc:  # pragma: no cover - network-heavy
        log.warning(
            "LLM request failed, using fallback",
            extra={"trace_id": trace_id, "error": str(exc)},
        )
        payload = fallback
        if hasattr(payload, "model_dump"):
            payload = payload.model_dump()
        if isinstance(payload, str):
            return payload
        return json.dumps(payload)
