from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List


HistoryMessage = dict[str, str]


class LLMClient(ABC):
    """LLM interface so providers can be swapped at runtime."""

    @abstractmethod
    def reply(self, history: List[HistoryMessage]) -> str:  # pragma: no cover - interface
        raise NotImplementedError
