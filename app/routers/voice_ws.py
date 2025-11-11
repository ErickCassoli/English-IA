from __future__ import annotations

import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services import tts_stub
from app.utils import ids

router = APIRouter(tags=["voice"])


@router.websocket("/ws/call")
async def call_coach(websocket: WebSocket) -> None:
    await websocket.accept()
    trace_id = ids.new_trace_id()
    try:
        payload_raw = await websocket.receive_text()
        meta = json.loads(payload_raw)
    except WebSocketDisconnect:  # pragma: no cover - transport detail
        return
    except json.JSONDecodeError:
        meta = {}
    reply = {
        "trace_id": trace_id,
        "reply": "Hi there! Let's work on your pronunciation today.",
        "tips": [
            "Slow down and stress content words.",
            "Record yourself and compare with natives.",
        ],
        "focus_tags": [meta.get("topic", "conversation")],
        "audio_base64": tts_stub.synthesize_beep_base64(),
    }
    await websocket.send_json(reply)
    await websocket.close()
