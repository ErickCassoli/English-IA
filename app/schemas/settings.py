from __future__ import annotations

from pydantic import BaseModel, Field


class SettingsResponse(BaseModel):
    llm_provider: str
    llm_model: str


class SettingsUpdateRequest(BaseModel):
    llm_provider: str = Field(pattern="^(simple_mock|ollama|openai)$")
    llm_model: str
