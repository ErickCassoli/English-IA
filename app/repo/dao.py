from __future__ import annotations

import json
from datetime import UTC, date, datetime
from typing import Any

from app.repo import db
from app.utils import ids


def _utc_now() -> str:
    return datetime.now(tz=UTC).isoformat()


def record_chat_message(
    trace_id: str,
    user_input: str,
    corrected: str,
    metadata: dict[str, Any] | None,
) -> None:
    conn = db.get_connection()
    conn.execute(
        """
        INSERT INTO messages (id, trace_id, user_input, corrected, metadata, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            ids.new_id(),
            trace_id,
            user_input,
            corrected,
            json.dumps(metadata or {}),
            _utc_now(),
        ),
    )
    conn.commit()
    _bump_stat("chats")


def record_error(trace_id: str, location: str, payload: dict[str, Any] | None, detail: str) -> None:
    conn = db.get_connection()
    conn.execute(
        """
        INSERT INTO prompt_errors (id, trace_id, location, payload, detail, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (ids.new_id(), trace_id, location, json.dumps(payload or {}), detail, _utc_now()),
    )
    conn.commit()


def create_quiz(trace_id: str, topic: str, questions: list[dict[str, Any]]) -> str:
    conn = db.get_connection()
    quiz_id = ids.new_id()
    now = _utc_now()
    conn.execute(
        "INSERT INTO quizzes (id, trace_id, topic, created_at) VALUES (?, ?, ?, ?)",
        (quiz_id, trace_id, topic, now),
    )
    for question in questions:
        conn.execute(
            """
            INSERT INTO quiz_items (id, quiz_id, prompt, options, answer, rationale, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                question["id"],
                quiz_id,
                question["prompt"],
                json.dumps(question["options"]),
                question["answer"],
                question["rationale"],
                now,
            ),
        )
    conn.commit()
    _bump_stat("quizzes")
    return quiz_id


def get_quiz(quiz_id: str) -> dict[str, Any] | None:
    conn = db.get_connection()
    quiz = conn.execute(
        "SELECT id, trace_id, topic FROM quizzes WHERE id = ?",
        (quiz_id,),
    ).fetchone()
    if not quiz:
        return None
    rows = conn.execute(
        "SELECT id, prompt, options, answer, rationale FROM quiz_items WHERE quiz_id = ?",
        (quiz_id,),
    ).fetchall()
    questions = [
        {
            "id": row["id"],
            "prompt": row["prompt"],
            "options": json.loads(row["options"]),
            "answer": row["answer"],
            "rationale": row["rationale"],
        }
        for row in rows
    ]
    return {
        "id": quiz_id,
        "trace_id": quiz["trace_id"],
        "topic": quiz["topic"],
        "questions": questions,
    }


def ensure_flashcard(front: str, back: str, tag: str | None = None) -> str:
    conn = db.get_connection()
    row = conn.execute(
        "SELECT id FROM flashcards WHERE front = ? AND back = ?",
        (front, back),
    ).fetchone()
    if row:
        return row["id"]
    card_id = ids.new_id()
    now = _utc_now()
    conn.execute(
        """
        INSERT INTO flashcards (
            id,
            front,
            back,
            tag,
            repetitions,
            interval,
            easiness,
            due_at,
            created_at
        )
        VALUES (?, ?, ?, ?, 0, 0, 2.5, ?, ?)
        """,
        (card_id, front, back, tag, now, now),
    )
    conn.commit()
    return card_id


def get_flashcards_due(limit: int = 10) -> list[dict[str, Any]]:
    conn = db.get_connection()
    now = _utc_now()
    rows = conn.execute(
        """
        SELECT id, front, back, tag, repetitions, interval, easiness, due_at
        FROM flashcards
        WHERE due_at <= ?
        ORDER BY due_at ASC
        LIMIT ?
        """,
        (now, limit),
    ).fetchall()
    return [
        {
            "id": row["id"],
            "front": row["front"],
            "back": row["back"],
            "tag": row["tag"],
            "repetitions": row["repetitions"],
            "interval": row["interval"],
            "easiness": row["easiness"],
            "due_at": row["due_at"],
        }
        for row in rows
    ]


def get_flashcard(card_id: str) -> dict[str, Any] | None:
    conn = db.get_connection()
    row = conn.execute(
        """
        SELECT id, front, back, tag, repetitions, interval, easiness, due_at
        FROM flashcards
        WHERE id = ?
        """,
        (card_id,),
    ).fetchone()
    if not row:
        return None
    return dict(row)


def update_flashcard_state(
    *,
    card_id: str,
    repetitions: int,
    interval: int,
    easiness: float,
    due_at: datetime,
) -> None:
    conn = db.get_connection()
    conn.execute(
        """
        UPDATE flashcards
        SET repetitions = ?, interval = ?, easiness = ?, due_at = ?
        WHERE id = ?
        """,
        (repetitions, interval, easiness, due_at.isoformat(), card_id),
    )
    conn.commit()
    _bump_stat("flashcards")


def get_stats_summary() -> dict[str, int]:
    conn = db.get_connection()
    totals = conn.execute(
        """
        SELECT
            COALESCE(SUM(chats), 0) AS chats,
            COALESCE(SUM(quizzes), 0) AS quizzes,
            COALESCE(SUM(flashcards), 0) AS flashcards
        FROM stats_daily
        """
    ).fetchone()
    flashcards_due = conn.execute(
        "SELECT COUNT(*) AS due FROM flashcards WHERE due_at <= ?",
        (_utc_now(),),
    ).fetchone()
    flashcards_total = conn.execute("SELECT COUNT(*) AS total FROM flashcards").fetchone()
    return {
        "chats": totals["chats"],
        "quizzes": totals["quizzes"],
        "flashcards": totals["flashcards"],
        "flashcards_due": flashcards_due["due"],
        "total_flashcards": flashcards_total["total"],
    }


def create_user(*, email: str, password_hash: str, display_name: str) -> dict[str, Any]:
    conn = db.get_connection()
    user_id = ids.new_id()
    now = _utc_now()
    conn.execute(
        """
        INSERT INTO users (id, email, password_hash, display_name, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (user_id, email, password_hash, display_name, now),
    )
    conn.commit()
    return {"id": user_id, "email": email, "display_name": display_name}


def get_user_by_email(email: str) -> dict[str, Any] | None:
    conn = db.get_connection()
    row = conn.execute(
        "SELECT id, email, password_hash, display_name FROM users WHERE email = ?",
        (email,),
    ).fetchone()
    if not row:
        return None
    return dict(row)


def _bump_stat(kind: str) -> None:
    statements = {
        "chats": """
            INSERT INTO stats_daily (date, chats, quizzes, flashcards)
            VALUES (?, 0, 0, 0)
            ON CONFLICT(date) DO UPDATE SET chats = stats_daily.chats + 1
            """,
        "quizzes": """
            INSERT INTO stats_daily (date, chats, quizzes, flashcards)
            VALUES (?, 0, 0, 0)
            ON CONFLICT(date) DO UPDATE SET quizzes = stats_daily.quizzes + 1
            """,
        "flashcards": """
            INSERT INTO stats_daily (date, chats, quizzes, flashcards)
            VALUES (?, 0, 0, 0)
            ON CONFLICT(date) DO UPDATE SET flashcards = stats_daily.flashcards + 1
            """,
    }
    query = statements[kind]
    conn = db.get_connection()
    today = date.today().isoformat()
    conn.execute(query, (today,))
    conn.commit()
