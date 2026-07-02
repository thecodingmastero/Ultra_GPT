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

    @abstractmethod
    def get_chart(self, symbol: str, resolution: str = "D", count: int = 30) -> dict:
        """Return OHLCV candle data for a symbol.

        Expected return format::

            {
                "symbol": "AAPL",
                "resolution": "D",
                "candles": [
                    {"t": <unix_timestamp>, "o": <open>, "h": <high>,
                     "l": <low>, "c": <close>, "v": <volume>},
                    ...
                ],
            }
        """
