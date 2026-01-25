from __future__ import annotations

from pydantic import BaseModel, Field


class SettingsResponse(BaseModel):
    llm_provider: str
    llm_model: str
    native_language: str = "pt-BR"
    target_language: str = "en"


class SettingsUpdateRequest(BaseModel):
    llm_provider: str = Field(pattern="^(simple_mock|ollama|openai)$")
    llm_model: str
    native_language: str = "pt-BR"
    target_language: str = "en"
