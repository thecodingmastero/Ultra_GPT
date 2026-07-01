from __future__ import annotations

import requests

from backend.app.providers.market_data.base import MarketDataProvider, MarketDataProviderError


class FinnhubMarketDataProvider(MarketDataProvider):
    BASE_URL = "https://finnhub.io/api/v1"

    def __init__(self, api_key: str = "") -> None:
        self.api_key = api_key

    def _request(self, path: str, params: dict[str, str]) -> dict:
        if not self.api_key:
            raise MarketDataProviderError("FINNHUB_API_KEY is not configured.")
        response = requests.get(
            f"{self.BASE_URL}/{path}",
            params={**params, "token": self.api_key},
            timeout=10,
        )
        if response.status_code == 429:
            raise MarketDataProviderError("Finnhub rate limit reached. Please try again shortly.")
        try:
            response.raise_for_status()
        except requests.RequestException as exc:
            raise MarketDataProviderError("Finnhub request failed.") from exc
        data = response.json()
        if isinstance(data, dict) and "error" in data:
            error_text = str(data["error"]).lower()
            if "api key" in error_text or "token" in error_text:
                raise MarketDataProviderError("Finnhub API key is invalid or missing.")
            if "limit" in error_text:
                raise MarketDataProviderError("Finnhub rate limit reached. Please try again shortly.")
        return data

    def get_quote(self, symbol: str) -> dict:
        data = self._request("quote", {"symbol": symbol})
        if not data or data.get("c") in (None, 0):
            raise MarketDataProviderError(f"No quote data available for {symbol}.")
        return {
            "symbol": symbol.upper(),
            "current_price": round(float(data["c"]), 2),
            "daily_percent_change": round(float(data.get("dp", 0.0)), 2),
            "previous_close": round(float(data.get("pc", 0.0)), 2),
        }

    def get_company_profile(self, symbol: str) -> dict:
        data = self._request("stock/profile2", {"symbol": symbol})
        return {
            "symbol": symbol.upper(),
            "company_name": data.get("name") or symbol.upper(),
            "exchange": data.get("exchange") or "",
            "finnhub_industry": data.get("finnhubIndustry") or "",
        }
