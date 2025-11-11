from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


@router.websocket("/ws/call")
async def call_stub(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_json({"event": "start", "message": "voice mode stub"})
    try:
        while True:
            payload = await websocket.receive_text()
            await websocket.send_json({"event": "partial", "echo": payload})
    except WebSocketDisconnect:
        pass
    finally:
        try:
            await websocket.send_json({"event": "final", "message": "call ended"})
        except RuntimeError:
            pass
        await websocket.close()
