from __future__ import annotations

from backend.app.services.market_data.base import MarketDataProvider, MarketDataProviderError
from backend.app.services.market_data.cache import TTLCache

_QUOTE_TTL = 60.0   # seconds — quotes refresh every minute
_PROFILE_TTL = 3600.0  # seconds — company profiles change rarely
_CHART_TTL = 300.0   # seconds — chart candles refresh every 5 minutes


class MarketDataService:
    def __init__(
        self,
        provider: MarketDataProvider,
        quote_cache: TTLCache | None = None,
        profile_cache: TTLCache | None = None,
        chart_cache: TTLCache | None = None,
    ) -> None:
        self.provider = provider
        self._quote_cache = quote_cache or TTLCache(ttl=_QUOTE_TTL)
        self._profile_cache = profile_cache or TTLCache(ttl=_PROFILE_TTL)
        self._chart_cache = chart_cache or TTLCache(ttl=_CHART_TTL)

    def get_quote(self, symbol: str) -> dict:
        cleaned_symbol = symbol.strip().upper()
        if not cleaned_symbol:
            raise MarketDataProviderError("A stock symbol is required.")
        cached = self._quote_cache.get(cleaned_symbol)
        if cached is not None:
            return cached
        quote = self.provider.get_quote(cleaned_symbol)
        profile = self.provider.get_company_profile(cleaned_symbol)
        result = {**quote, "company_name": profile.get("company_name", cleaned_symbol)}
        self._quote_cache.set(cleaned_symbol, result)
        return result

    def get_company_profile(self, symbol: str) -> dict:
        cleaned_symbol = symbol.strip().upper()
        if not cleaned_symbol:
            raise MarketDataProviderError("A stock symbol is required.")
        cached = self._profile_cache.get(cleaned_symbol)
        if cached is not None:
            return cached
        profile = self.provider.get_company_profile(cleaned_symbol)
        self._profile_cache.set(cleaned_symbol, profile)
        return profile

    def get_chart(self, symbol: str, resolution: str = "D", count: int = 30) -> dict:
        """Return OHLCV candle data for *symbol*.

        Resolution: 'D' = daily (default), 'W' = weekly, 'M' = monthly.
        Count: number of candles to return (default 30).
        """
        cleaned_symbol = symbol.strip().upper()
        if not cleaned_symbol:
            raise MarketDataProviderError("A stock symbol is required.")
        cache_key = f"{cleaned_symbol}:{resolution}:{count}"
        cached = self._chart_cache.get(cache_key)
        if cached is not None:
            return cached
        chart = self.provider.get_chart(cleaned_symbol, resolution=resolution, count=count)
        self._chart_cache.set(cache_key, chart)
        return chart
