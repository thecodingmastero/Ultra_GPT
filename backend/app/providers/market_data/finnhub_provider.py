from __future__ import annotations

import math
import time

import requests

from backend.app.providers.market_data.base import MarketDataProvider, MarketDataProviderError

_MAX_RETRIES = 2
_RETRY_BACKOFF = 0.5  # seconds between retries


class FinnhubMarketDataProvider(MarketDataProvider):
    BASE_URL = "https://finnhub.io/api/v1"

    def __init__(self, api_key: str = "") -> None:
        self.api_key = api_key

    def _request(self, path: str, params: dict[str, str]) -> dict:
        if not self.api_key:
            raise MarketDataProviderError("FINNHUB_API_KEY is not configured.")
        last_exc: Exception | None = None
        for attempt in range(_MAX_RETRIES + 1):
            try:
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
            except MarketDataProviderError:
                raise
            except Exception as exc:
                last_exc = exc
                if attempt < _MAX_RETRIES:
                    time.sleep(_RETRY_BACKOFF * (attempt + 1))
        raise MarketDataProviderError("Finnhub request failed after retries.") from last_exc

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

    def get_chart(self, symbol: str, resolution: str = "D", count: int = 30) -> dict:
        """Return OHLCV daily candles for *symbol* from Finnhub /stock/candle."""
        now = int(time.time())
        # Approximate: D=1 day, W=7 days, M=30 days per candle
        days_per_candle = {"D": 1, "W": 7, "M": 30}.get(resolution, 1)
        # Add buffer for weekends/holidays (~1.5x)
        from_ts = now - int(count * days_per_candle * 1.5 * 86400)
        data = self._request(
            "stock/candle",
            {"symbol": symbol, "resolution": resolution, "from": str(from_ts), "to": str(now)},
        )
        status = data.get("s", "no_data")
        if status == "no_data" or not data.get("c"):
            return {"symbol": symbol.upper(), "resolution": resolution, "candles": []}
        timestamps: list[int] = data.get("t", [])
        opens: list[float] = data.get("o", [])
        highs: list[float] = data.get("h", [])
        lows: list[float] = data.get("l", [])
        closes: list[float] = data.get("c", [])
        volumes: list[int] = data.get("v", [])
        candles = [
            {
                "t": timestamps[i],
                "o": round(opens[i], 2),
                "h": round(highs[i], 2),
                "l": round(lows[i], 2),
                "c": round(closes[i], 2),
                "v": volumes[i] if i < len(volumes) else 0,
            }
            for i in range(len(timestamps))
            if not math.isnan(closes[i])
        ]
        return {"symbol": symbol.upper(), "resolution": resolution, "candles": candles[-count:]}
