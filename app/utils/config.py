from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


class Settings(BaseModel):
    app_name: str = "english-ia"
    environment: str = "local"
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llama3"
    db_url: str = "sqlite:///./english_ia.db"
    allowed_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:8000",
            "http://localhost:8501",
        ]
    )

    @classmethod
    def from_env(cls) -> Settings:
        data = {
            "environment": os.getenv("ENVIRONMENT", "local"),
            "ollama_host": os.getenv("OLLAMA_HOST", "http://localhost:11434"),
            "ollama_model": os.getenv("OLLAMA_MODEL", "llama3"),
            "db_url": os.getenv("DB_URL", "sqlite:///./english_ia.db"),
        }
        origins = os.getenv("ALLOWED_ORIGINS")
        if origins:
            data["allowed_origins"] = [
                origin.strip() for origin in origins.split(",") if origin.strip()
            ]
        return cls(**data)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings.from_env()
