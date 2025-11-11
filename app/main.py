from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.repo.db import init_db
from app.routers.auth import router as auth_router
from app.routers.chat import router as chat_router
from app.routers.flashcards import router as flashcards_router
from app.routers.quiz import router as quiz_router
from app.routers.stats import router as stats_router
from app.utils import ids
from app.utils.config import get_settings
from app.utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    logger.info("database initialized")
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="English IA API",
        version="0.1.0",
        description="Backend services for the English IA project.",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(chat_router)
    app.include_router(quiz_router)
    app.include_router(flashcards_router)
    app.include_router(stats_router)
    app.include_router(auth_router)

    @app.get("/healthz", tags=["health"])
    async def healthcheck():
        return {"status": "ok", "trace_id": ids.new_trace_id()}

    return app


app = create_app()
