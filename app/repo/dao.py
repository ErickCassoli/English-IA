from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from typing import Any

from app.repo import db
from app.utils import ids


def _utc_now() -> str:
    return datetime.now(tz=UTC).isoformat()


def _today() -> str:
    return datetime.now(tz=UTC).date().isoformat()


def record_message(trace_id: str, user_input: str, corrected: str, metadata: dict[str, Any] | None) -> None:
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


def record_error(trace_id: str, location: str, payload: dict[str, Any] | None, detail: str) -> None:
    conn = db.get_connection()
    conn.execute(
        """
        INSERT INTO errors (id, trace_id, location, payload, detail, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            ids.new_id(),
            trace_id,
            location,
            json.dumps(payload or {}),
            detail,
            _utc_now(),
        ),
    )
    conn.commit()


def create_quiz(trace_id: str, topic: str, difficulty: str, questions: list[dict[str, Any]]) -> str:
    conn = db.get_connection()
    quiz_id = ids.new_id()
    now = _utc_now()
    conn.execute(
        """
        INSERT INTO quizzes (id, trace_id, topic, difficulty, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (quiz_id, trace_id, topic, difficulty, now),
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
    return quiz_id


def get_quiz(quiz_id: str) -> dict[str, Any] | None:
    conn = db.get_connection()
    quiz = conn.execute(
        "SELECT id, trace_id, topic, difficulty FROM quizzes WHERE id = ?",
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
        "id": quiz["id"],
        "trace_id": quiz["trace_id"],
        "topic": quiz["topic"],
        "difficulty": quiz["difficulty"],
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
        INSERT INTO flashcards (id, front, back, tag, repetitions, interval, easiness, due_at, created_at)
        VALUES (?, ?, ?, ?, 0, 0, 2.5, ?, ?)
        """,
        (card_id, front, back, tag, now, now),
    )
    conn.commit()
    return card_id


def get_flashcards_due(limit: int = 10) -> list[dict[str, Any]]:
    conn = db.get_connection()
    rows = conn.execute(
        """
        SELECT id, front, back, tag, repetitions, interval, easiness, due_at
        FROM flashcards
        WHERE due_at <= ?
        ORDER BY due_at ASC
        LIMIT ?
        """,
        (_utc_now(), limit),
    ).fetchall()
    return [dict(row) for row in rows]


def update_flashcard_state(card_id: str, repetitions: int, interval: int, easiness: float, due_at: datetime) -> None:
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


def bump_daily_stats(minutes: int, accuracy: float, error_tag: str | None = None) -> None:
    conn = db.get_connection()
    today = _today()
    row = conn.execute("SELECT minutes, accuracy, errors FROM stats_daily WHERE date = ?", (today,)).fetchone()
    if row:
        total_minutes = row["minutes"] + minutes
        avg_accuracy = (row["accuracy"] + accuracy) / 2
        errors = json.loads(row["errors"] or "[]")
    else:
        total_minutes = minutes
        avg_accuracy = accuracy
        errors = []
    if error_tag:
        errors.append(error_tag)
    conn.execute(
        """
        INSERT INTO stats_daily (date, minutes, accuracy, errors)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(date) DO UPDATE SET
            minutes = excluded.minutes,
            accuracy = excluded.accuracy,
            errors = excluded.errors
        """,
        (today, total_minutes, avg_accuracy, json.dumps(errors)),
    )
    conn.commit()


def get_stats_summary() -> dict[str, Any]:
    conn = db.get_connection()
    seven_days_ago = datetime.now(tz=UTC).date() - timedelta(days=6)
    rows = conn.execute(
        "SELECT minutes, accuracy, errors FROM stats_daily WHERE date >= ?",
        (seven_days_ago.isoformat(),),
    ).fetchall()
    minutes = sum(row["minutes"] for row in rows)
    accuracy_values = [row["accuracy"] for row in rows if row["accuracy"]]
    accuracy = round(sum(accuracy_values) / len(accuracy_values), 2) if accuracy_values else 0.0
    tag_counter: dict[str, int] = {}
    for row in rows:
        tags = json.loads(row["errors"] or "[]")
        for tag in tags:
            tag_counter[tag] = tag_counter.get(tag, 0) + 1
    top_tags = sorted(tag_counter, key=tag_counter.get, reverse=True)[:3]
    return {
        "last_7_days_minutes": minutes,
        "accuracy_estimate": accuracy,
        "top_error_tags": top_tags,
    }
