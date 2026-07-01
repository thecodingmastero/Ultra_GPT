from __future__ import annotations

from abc import ABC, abstractmethod


class MarketDataProviderError(RuntimeError):
    pass


class MarketDataProvider(ABC):
    @abstractmethod
    def get_quote(self, symbol: str) -> dict:
        """Return market quote details for a symbol."""

    @abstractmethod
    def get_company_profile(self, symbol: str) -> dict:
        """Return company profile details for a symbol."""
