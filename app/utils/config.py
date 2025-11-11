from __future__ import annotations

import os
from functools import lru_cache
from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field, field_validator

load_dotenv()


class Settings(BaseModel):
    """Runtime configuration resolved from environment variables or defaults."""

    model_config = ConfigDict(populate_by_name=True)

    backend_host: str = Field(default="0.0.0.0", alias="BACKEND_HOST")
    backend_port: int = Field(default=8000, alias="BACKEND_PORT")
    database_url: str = Field(default="sqlite:///./data.db", alias="DATABASE_URL")
    default_llm_provider: Literal["simple_mock", "ollama", "openai"] = Field(
        default="simple_mock", alias="DEFAULT_LLM_PROVIDER"
    )
    default_llm_model: str = Field(default="mock-1", alias="DEFAULT_LLM_MODEL")
    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:8000"])

    @field_validator("cors_origins", mode="before")
    def _split_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, list):
            return value
        if not value:
            return ["http://localhost:8000"]
        return [origin.strip() for origin in value.split(",") if origin.strip()]

    @classmethod
    def from_env(cls) -> Settings:
        data: dict[str, object] = {}
        for name, field in cls.model_fields.items():
            env_name = field.alias or name
            if env_name in os.environ:
                data[name] = os.environ[env_name]
        if "CORS_ORIGINS" in os.environ:
            data["cors_origins"] = os.environ["CORS_ORIGINS"]
        return cls(**data)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings.from_env()
