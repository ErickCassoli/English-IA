from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    corrected: str
    explanation: str
    highlights: list[dict[str, int]]
    tags: list[str]


@router.post("/correct", response_model=ChatResponse)
async def correct_message(_: ChatRequest) -> ChatResponse:
    return ChatResponse(
        corrected="stub",
        explanation="not implemented",
        highlights=[],
        tags=["stub"],
    )
