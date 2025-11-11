from __future__ import annotations

from app.repo.models import LLMProvider, Settings as SettingsModel
from app.services.llm.base import LLMClient
from app.services.llm.ollama import OllamaClient
from app.services.llm.openai import OpenAIClient
from app.services.llm.simple_mock import SimpleMockClient
from app.utils.config import get_settings

runtime_settings = get_settings()


def get_llm(settings_row: SettingsModel | None) -> LLMClient:
    provider = settings_row.llm_provider if settings_row else LLMProvider(runtime_settings.default_llm_provider)
    model = settings_row.llm_model if settings_row else runtime_settings.default_llm_model

    if provider == LLMProvider.OLLAMA:
        return OllamaClient(runtime_settings.ollama_base_url, model)
    if provider == LLMProvider.OPENAI:
        try:
            return OpenAIClient(runtime_settings.openai_api_key or "", model)
        except ValueError:
            return SimpleMockClient()
    return SimpleMockClient()
