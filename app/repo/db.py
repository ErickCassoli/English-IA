from __future__ import annotations

import sqlite3
from pathlib import Path

from app.utils.config import get_settings
from app.utils.logger import get_logger

settings = get_settings()
log = get_logger(__name__)
_connection: sqlite3.Connection | None = None


def _resolve_path() -> Path:
    if not settings.db_url.startswith("sqlite:///"):
        raise ValueError("Only sqlite:/// URLs are supported in the MVP")
    raw_path = settings.db_url.removeprefix("sqlite:///")
    path = Path(raw_path)
    if not path.is_absolute():
        path = Path.cwd() / path
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def get_connection() -> sqlite3.Connection:
    global _connection
    if _connection is None:
        db_path = _resolve_path()
        _connection = sqlite3.connect(db_path, check_same_thread=False)
        _connection.row_factory = sqlite3.Row
        log.info("sqlite connection ready", extra={"trace_id": "bootstrap", "path": str(db_path)})
    return _connection


def init_db() -> None:
    conn = get_connection()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            device TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            trace_id TEXT NOT NULL,
            user_input TEXT NOT NULL,
            corrected TEXT NOT NULL,
            metadata TEXT,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS errors (
            id TEXT PRIMARY KEY,
            trace_id TEXT NOT NULL,
            location TEXT NOT NULL,
            payload TEXT,
            detail TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS quizzes (
            id TEXT PRIMARY KEY,
            trace_id TEXT NOT NULL,
            topic TEXT NOT NULL,
            difficulty TEXT,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS quiz_items (
            id TEXT PRIMARY KEY,
            quiz_id TEXT NOT NULL REFERENCES quizzes(id) ON DELETE CASCADE,
            prompt TEXT NOT NULL,
            options TEXT NOT NULL,
            answer TEXT NOT NULL,
            rationale TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS flashcards (
            id TEXT PRIMARY KEY,
            front TEXT NOT NULL,
            back TEXT NOT NULL,
            tag TEXT,
            repetitions INTEGER NOT NULL DEFAULT 0,
            interval INTEGER NOT NULL DEFAULT 0,
            easiness REAL NOT NULL DEFAULT 2.5,
            due_at TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS stats_daily (
            date TEXT PRIMARY KEY,
            minutes INTEGER NOT NULL DEFAULT 0,
            accuracy REAL NOT NULL DEFAULT 0,
            errors TEXT
        );
        """
    )
    conn.commit()
