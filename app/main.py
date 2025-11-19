from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.repo.db import init_db, session_scope, upgrade_db
from app.repo.seed import seed_defaults
from app.routers import (
    chat,
    dashboard,
    flashcards,
    health,
    practice,
    quiz,
    reports,
    sessions,
    settings as settings_router,
)
from app.utils.config import get_settings
from app.ws import call as call_ws

app_settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    upgrade_db()
    init_db()
    with session_scope() as db:
        seed_defaults(db)
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="English IA", version="0.2.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=app_settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health.router)
    app.include_router(practice.router)
    app.include_router(sessions.router)
    app.include_router(chat.router)
    app.include_router(quiz.router)
    app.include_router(reports.router)
    app.include_router(flashcards.router)
    app.include_router(dashboard.router)
    app.include_router(settings_router.router)
    app.include_router(call_ws.router)
    return app


app = create_app()
