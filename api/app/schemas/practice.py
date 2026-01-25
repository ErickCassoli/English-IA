from __future__ import annotations

from pydantic import BaseModel


class PracticeTopicSchema(BaseModel):
    code: str
    label: str
    description: str
