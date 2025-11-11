from __future__ import annotations

from typing import Any, Dict

from pydantic import BaseModel


class DashboardSummary(BaseModel):
    last_session: Dict[str, Any]
    totals: Dict[str, Any]
    due_count: int
