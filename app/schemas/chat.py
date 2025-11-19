from __future__ import annotations

from pydantic import BaseModel


class ChatMessageRequest(BaseModel):
    text: str


class DetectedErrorSchema(BaseModel):
    start: int
    end: int
    category: str
    user_text: str
    corrected_text: str
    note: str


class ChatMessageResponse(BaseModel):
    reply: str
    detected_errors: list[DetectedErrorSchema]
