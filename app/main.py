from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.repo.db import init_db
from app.routers import chat, flashcards, quiz, stats, voice_ws
from app.utils import ids
from app.utils.config import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="English IA", version="0.1.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(chat.router)
    app.include_router(quiz.router)
    app.include_router(flashcards.router)
    app.include_router(stats.router)
    app.include_router(voice_ws.router)

    @app.get("/healthz")
    async def healthz():
        return {"status": "ok", "trace_id": ids.new_trace_id()}

    return app


app = create_app()
