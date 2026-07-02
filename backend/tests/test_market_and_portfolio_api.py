from __future__ import annotations

from backend.app.services.market_data.base import MarketDataProvider, MarketDataProviderError


class BrokenMarketDataProvider(MarketDataProvider):
    def get_quote(self, symbol: str) -> dict:
        raise MarketDataProviderError("provider unavailable")

    def get_company_profile(self, symbol: str) -> dict:
        raise MarketDataProviderError("provider unavailable")

    def get_chart(self, symbol: str, resolution: str = "D", count: int = 30) -> dict:
        raise MarketDataProviderError("provider unavailable")


def test_market_quote_returns_company_name_and_price(client):
    response = client.get("/api/market/quote?symbol=AAPL")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["company_name"] == "AAPL Incorporated"
    assert payload["current_price"] == 200.0


def test_market_profile_endpoint_returns_company_metadata(client):
    response = client.get("/api/market/profile?symbol=AAPL")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["company_name"] == "AAPL Incorporated"
    assert payload["finnhub_industry"] == "Technology"


def test_portfolio_analysis_returns_weights_and_risk_flags(client):
    response = client.post(
        "/api/portfolio/analyze",
        json={
            "holdings": [
                {"symbol": "AAPL", "quantity": 4},
                {"symbol": "MSFT", "quantity": 1},
            ]
        },
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["summary"]["position_count"] == 2
    assert payload["positions"][0]["symbol"] == "AAPL"
    assert payload["positions"][0]["weight"] > 0.8
    assert payload["sector_breakdown"][0]["sector"] == "Technology"
    assert payload["risk_flags"]


def test_market_quote_returns_graceful_error_when_provider_fails(client):
    original_provider = client.application.config["MARKET_DATA_PROVIDER_INSTANCE"]
    client.application.config["MARKET_DATA_PROVIDER_INSTANCE"] = BrokenMarketDataProvider()
    try:
        response = client.get("/api/market/quote?symbol=AAPL")
    finally:
        client.application.config["MARKET_DATA_PROVIDER_INSTANCE"] = original_provider

    assert response.status_code == 502
    assert "Unable to fetch market data right now" in response.get_json()["error"]


def test_portfolio_analysis_rejects_invalid_input_with_safe_message(client):
    response = client.post("/api/portfolio/analyze", json={"holdings": [{"symbol": "AAPL", "quantity": 0}]})

    assert response.status_code == 400
    assert "Invalid portfolio input" in response.get_json()["error"]
