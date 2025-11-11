from __future__ import annotations

import json

from app.services import llm


async def _fake_generate(*_, **__):
    return json.dumps(
        {
            "corrected": "Hello there!",
            "explanation": "Capitalization fix",
            "highlights": [{"from_index": 0, "to_index": 5, "note": "Greeting"}],
            "tags": ["mechanics"],
        }
    )


def test_chat_contract(monkeypatch, client):
    monkeypatch.setattr(llm, "generate", _fake_generate)
    response = client.post(
        "/api/chat/correct",
        json={"message": "hello there", "focus": ["grammar"]},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["corrected"] == "Hello there!"
    assert payload["explanation"]
    assert payload["trace_id"]
