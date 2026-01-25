from __future__ import annotations

from app.repo.models import LLMProvider, Settings as SettingsModel
from app.services.llm.base import LLMClient
from app.services.llm.ollama import OllamaClient
from app.services.llm.openai import OpenAIClient
from app.services.llm.simple_mock import SimpleMockClient
from app.utils.config import Settings, get_settings

runtime_settings = get_settings()


def get_llm(settings_row: SettingsModel | None, config: Settings | None = None) -> LLMClient:
    cfg = config or runtime_settings
    provider_value = settings_row.llm_provider if settings_row else cfg.default_llm_provider
    try:
        provider = LLMProvider(provider_value)
    except ValueError:
        provider = LLMProvider.SIMPLE
    model = settings_row.llm_model if settings_row else cfg.default_llm_model

    if provider == LLMProvider.OLLAMA:
        return OllamaClient(cfg.ollama_base_url, model)
    if provider == LLMProvider.OPENAI:
        try:
            return OpenAIClient(cfg.openai_api_key or "", model)
        except ValueError:
            return SimpleMockClient()
    return SimpleMockClient()
