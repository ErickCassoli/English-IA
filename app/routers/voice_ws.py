from __future__ import annotations

from fastapi import APIRouter, WebSocket

router = APIRouter()


@router.websocket("/ws/call")
async def call_coach(_: WebSocket) -> None:  # pragma: no cover - stub
    raise RuntimeError("Voice stub not implemented yet")
