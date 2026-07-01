from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence


class AIProvider(ABC):
    @abstractmethod
    def chat(self, messages: Sequence[dict[str, str]]) -> str:
        """Return an education-first assistant response."""
