from __future__ import annotations

import json
from typing import Any

import httpx

from app.utils.config import get_settings
from app.utils.logger import get_logger

settings = get_settings()
log = get_logger(__name__)


async def generate(prompt: str, trace_id: str, fallback: dict[str, Any]) -> str:
    payload = {"model": settings.ollama_model, "prompt": prompt, "stream": False}
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(f"{settings.ollama_host.rstrip('/')}/api/generate", json=payload)
            response.raise_for_status()
            data = response.json()
            text = data.get("response") or data.get("output")
            if not text:
                raise ValueError("empty response")
            return text
    except Exception as exc:  # pragma: no cover - network fallback
        log.warning("ollama unavailable, falling back", extra={"trace_id": trace_id, "error": str(exc)})
        return json.dumps(fallback)
