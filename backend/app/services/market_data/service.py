from __future__ import annotations

from backend.app.services.market_data.base import MarketDataProvider, MarketDataProviderError


class MarketDataService:
    def __init__(self, provider: MarketDataProvider) -> None:
        self.provider = provider

    def get_quote(self, symbol: str) -> dict:
        cleaned_symbol = symbol.strip().upper()
        if not cleaned_symbol:
            raise MarketDataProviderError("A stock symbol is required.")
        quote = self.provider.get_quote(cleaned_symbol)
        profile = self.provider.get_company_profile(cleaned_symbol)
        return {**quote, "company_name": profile.get("company_name", cleaned_symbol)}
