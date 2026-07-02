from __future__ import annotations

import pytest

from backend.app import create_app
from backend.app.extensions import db
from backend.app.services.ai.base import AIProvider
from backend.app.services.market_data.base import MarketDataProvider


class TestConfig:
    TESTING = True
    SECRET_KEY = "test-secret"
    JWT_SECRET_KEY = "test-jwt"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    AI_PROVIDER = "openai"
    MARKET_DATA_PROVIDER = "finnhub"


class FakeAIProvider(AIProvider):
    def chat(self, messages):
        return "Educational response about diversification and long-term investing."


class FakeMarketDataProvider(MarketDataProvider):
    def get_quote(self, symbol: str) -> dict:
        prices = {
            "AAPL": {"symbol": "AAPL", "current_price": 200.0, "daily_percent_change": 1.2, "previous_close": 197.0},
            "MSFT": {"symbol": "MSFT", "current_price": 100.0, "daily_percent_change": -0.3, "previous_close": 100.3},
            "VOO": {"symbol": "VOO", "current_price": 400.0, "daily_percent_change": 0.5, "previous_close": 398.0},
        }
        if symbol not in prices:
            from backend.app.services.market_data.base import MarketDataProviderError
            raise MarketDataProviderError(f"No quote data available for {symbol}.")
        return prices[symbol]

    def get_company_profile(self, symbol: str) -> dict:
        industries = {"AAPL": "Technology", "MSFT": "Technology", "VOO": "ETF"}
        return {"symbol": symbol, "company_name": f"{symbol} Incorporated", "finnhub_industry": industries.get(symbol, "")}

    def get_chart(self, symbol: str, resolution: str = "D", count: int = 30) -> dict:
        candles = [
            {"t": 1700000000 + i * 86400, "o": 195.0 + i, "h": 202.0 + i, "l": 193.0 + i, "c": 198.0 + i, "v": 1000000}
            for i in range(count)
        ]
        return {"symbol": symbol.upper(), "resolution": resolution, "candles": candles}


@pytest.fixture()
def app():
    app = create_app(TestConfig)
    app.config["AI_PROVIDER_INSTANCE"] = FakeAIProvider()
    app.config["MARKET_DATA_PROVIDER_INSTANCE"] = FakeMarketDataProvider()

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()
