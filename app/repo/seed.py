from __future__ import annotations

from sqlalchemy.orm import Session

from app.repo import dao


def seed_defaults(db: Session) -> None:
    """Ensure a default user and settings row exist."""
    dao.ensure_default_user(db)
    dao.get_settings(db)
