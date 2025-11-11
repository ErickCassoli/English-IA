from __future__ import annotations

from datetime import UTC, datetime


def utc_now() -> datetime:
    """Return a timezone-aware UTC datetime."""
    return datetime.now(tz=UTC)


def iso_now() -> str:
    """Return current UTC time in ISO format."""
    return utc_now().isoformat()
