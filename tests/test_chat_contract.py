import json

from app.services import llm


def test_chat_contract(monkeypatch, client):
    async def fake_generate_prompt(*args, **kwargs):
        return json.dumps(
            {
                "corrected": "Hello there!",
                "explanation": "Capitalization fix.",
                "highlights": [{"from_index": 0, "to_index": 5, "note": "Greeting"}],
                "tags": ["grammar"],
            }
        )

    monkeypatch.setattr(llm, "generate_prompt", fake_generate_prompt)
    response = client.post("/api/chat/correct", json={"message": "hello there"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["corrected"] == "Hello there!"
    assert payload["explanation"]
    assert payload["highlights"]
