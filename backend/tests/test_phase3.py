"""Phase 3 tests: market data caching, chart, portfolio volatility, entitlements, quest quiz/badges."""
from __future__ import annotations

import pytest

from backend.app.services.market_data.base import MarketDataProvider, MarketDataProviderError
from backend.app.services.market_data.cache import TTLCache


# ---------------------------------------------------------------------------
# TTLCache unit tests
# ---------------------------------------------------------------------------

def test_ttl_cache_set_and_get():
    cache = TTLCache(ttl=60)
    cache.set("KEY", {"value": 42})
    result = cache.get("KEY")
    assert result == {"value": 42}


def test_ttl_cache_miss_returns_none():
    cache = TTLCache(ttl=60)
    assert cache.get("MISSING") is None


def test_ttl_cache_expired_entry_returns_none():
    cache = TTLCache(ttl=-1)  # already expired
    cache.set("X", "data")
    assert cache.get("X") is None


def test_ttl_cache_clear():
    cache = TTLCache(ttl=60)
    cache.set("A", 1)
    cache.set("B", 2)
    assert len(cache) == 2
    cache.clear()
    assert len(cache) == 0


# ---------------------------------------------------------------------------
# Market data service caching integration
# ---------------------------------------------------------------------------

class CountingMarketDataProvider(MarketDataProvider):
    def __init__(self):
        self.quote_call_count = 0
        self.profile_call_count = 0
        self.chart_call_count = 0

    def get_quote(self, symbol: str) -> dict:
        self.quote_call_count += 1
        return {"symbol": symbol, "current_price": 100.0, "daily_percent_change": 0.0, "previous_close": 100.0}

    def get_company_profile(self, symbol: str) -> dict:
        self.profile_call_count += 1
        return {"symbol": symbol, "company_name": f"{symbol} Inc", "finnhub_industry": "Technology"}

    def get_chart(self, symbol: str, resolution: str = "D", count: int = 30) -> dict:
        self.chart_call_count += 1
        candles = [{"t": 1700000000 + i * 86400, "o": 99.0, "h": 101.0, "l": 98.0, "c": 100.0, "v": 5000} for i in range(count)]
        return {"symbol": symbol, "resolution": resolution, "candles": candles}


def test_market_service_caches_repeated_quote_calls(app):
    from backend.app.services.market_data.service import MarketDataService
    provider = CountingMarketDataProvider()
    service = MarketDataService(provider=provider)
    with app.app_context():
        service.get_quote("AAPL")
        service.get_quote("AAPL")
        service.get_quote("AAPL")
    assert provider.quote_call_count == 1


def test_market_service_caches_repeated_chart_calls(app):
    from backend.app.services.market_data.service import MarketDataService
    provider = CountingMarketDataProvider()
    service = MarketDataService(provider=provider)
    with app.app_context():
        service.get_chart("MSFT")
        service.get_chart("MSFT")
    assert provider.chart_call_count == 1


# ---------------------------------------------------------------------------
# Chart endpoint (now returns real OHLCV structure)
# ---------------------------------------------------------------------------

def test_market_chart_endpoint_returns_candles(client):
    response = client.get("/api/market/chart/AAPL")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["symbol"] == "AAPL"
    assert payload["resolution"] == "D"
    candles = payload["candles"]
    assert isinstance(candles, list)
    assert len(candles) == 30
    first = candles[0]
    assert {"t", "o", "h", "l", "c", "v"}.issubset(first.keys())


def test_market_chart_endpoint_respects_count_param(client):
    response = client.get("/api/market/chart/AAPL?count=10")
    assert response.status_code == 200
    assert len(response.get_json()["candles"]) == 10


def test_market_chart_endpoint_rejects_invalid_resolution(client):
    """Invalid resolution falls back to D gracefully."""
    response = client.get("/api/market/chart/AAPL?resolution=HOURLY")
    assert response.status_code == 200
    assert response.get_json()["resolution"] == "D"


# ---------------------------------------------------------------------------
# Portfolio analytics: volatility heuristic and learning suggestions
# ---------------------------------------------------------------------------

def test_portfolio_analysis_returns_diversification_score(client):
    response = client.post(
        "/api/portfolio/analyze",
        json={"holdings": [
            {"symbol": "AAPL", "quantity": 10},
            {"symbol": "MSFT", "quantity": 10},
            {"symbol": "VOO",  "quantity": 10},
        ]},
    )
    assert response.status_code == 200
    summary = response.get_json()["summary"]
    assert "diversification_score" in summary
    assert "volatility_label" in summary
    assert "hhi" in summary
    assert "sector_count" in summary


def test_portfolio_analysis_high_concentration_flagged_as_high_volatility(client):
    """A single-holding portfolio should trigger high volatility label."""
    response = client.post(
        "/api/portfolio/analyze",
        json={"holdings": [{"symbol": "AAPL", "quantity": 100}]},
    )
    assert response.status_code == 200
    summary = response.get_json()["summary"]
    assert summary["volatility_label"] == "high"
    assert summary["hhi"] == 1.0


def test_portfolio_analysis_includes_learning_suggestions(client):
    """Concentrated portfolio should include learning suggestions."""
    response = client.post(
        "/api/portfolio/analyze",
        json={"holdings": [
            {"symbol": "AAPL", "quantity": 9},
            {"symbol": "MSFT", "quantity": 1},
        ]},
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert "learning_suggestions" in payload
    suggestions = payload["learning_suggestions"]
    assert isinstance(suggestions, list)
    # Should suggest diversification-related lessons for concentrated portfolio
    slugs = [s["lesson_slug"] for s in suggestions]
    assert any("diversification" in slug or "risk" in slug for slug in slugs)


def test_portfolio_analysis_well_diversified_has_low_hhi(client):
    """Equal allocation across 3 different sectors -> lower HHI."""
    response = client.post(
        "/api/portfolio/analyze",
        json={"holdings": [
            {"symbol": "AAPL", "quantity": 1},  # Technology $200
            {"symbol": "VOO",  "quantity": 1},  # ETF $400
        ]},
    )
    assert response.status_code == 200
    summary = response.get_json()["summary"]
    # HHI < 0.5 indicates less concentration than single-holding
    assert summary["hhi"] < 1.0


# ---------------------------------------------------------------------------
# AI Policy: additional guardrail patterns
# ---------------------------------------------------------------------------

def test_assistant_blocks_urgency_buy_now_language(client):
    response = client.post("/api/assistant/chat", json={"message": "Should I buy now before it's too late?"})
    assert response.status_code == 200
    payload = response.get_json()
    # Either the urgency block or the directive block fires
    assert any(
        phrase in payload["response"]
        for phrase in ["can\u2019t encourage urgent", "can\u2019t provide direct buy/sell"]
    )


def test_assistant_blocks_pick_stock_for_me(client):
    response = client.post("/api/assistant/chat", json={"message": "Pick a stock for me to buy today."})
    assert response.status_code == 200
    assert "can\u2019t provide direct buy/sell" in response.get_json()["response"]


def test_assistant_blocks_no_risk_claim(client):
    response = client.post("/api/assistant/chat", json={"message": "Is there a no-risk investment strategy?"})
    assert response.status_code == 200
    assert "can\u2019t provide direct buy/sell" in response.get_json()["response"]


def test_assistant_allows_educational_question(client):
    """A purely educational question should pass through the policy."""
    response = client.post("/api/assistant/chat", json={"message": "What is a bond and how does it differ from a stock?"})
    assert response.status_code == 200
    payload = response.get_json()
    assert "response" in payload
    # Should not be the block response
    assert "can\u2019t provide" not in payload["response"]


def test_assistant_finalize_adds_disclaimer(client):
    """Responses that don't contain educational/financial advice text get disclaimer appended."""
    response = client.post("/api/assistant/chat", json={"message": "Tell me about compound interest."})
    assert response.status_code == 200
    payload = response.get_json()
    # Disclaimer must be accessible
    assert "disclaimer" in payload
    assert "educational purposes" in payload["disclaimer"].lower()


# ---------------------------------------------------------------------------
# Investor Quest: quiz submission, badge awarding
# ---------------------------------------------------------------------------

def _register_and_login_quest(client, email: str = "questp3@example.com") -> str:
    client.post(
        "/api/auth/register",
        json={"email": email, "password": "Pass1234!", "full_name": "Quest P3 User"},
    )
    resp = client.post("/api/auth/login", json={"email": email, "password": "Pass1234!"})
    return resp.get_json()["token"]


def test_quest_quiz_submit_high_score_awards_25_xp(client):
    token = _register_and_login_quest(client, "quizuser1@example.com")
    headers = {"Authorization": "Bearer " + token}
    response = client.post(
        "/api/quest/quiz/submit",
        json={"quiz_id": "diversification-quiz", "score": 90},
        headers=headers,
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["xp_awarded"] == 25
    assert payload["score"] == 90


def test_quest_quiz_submit_low_score_awards_5_xp(client):
    token = _register_and_login_quest(client, "quizuser2@example.com")
    headers = {"Authorization": "Bearer " + token}
    response = client.post(
        "/api/quest/quiz/submit",
        json={"quiz_id": "bonds-quiz", "score": 40},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.get_json()["xp_awarded"] == 5


def test_quest_quiz_submit_is_idempotent(client):
    token = _register_and_login_quest(client, "quizuser3@example.com")
    headers = {"Authorization": "Bearer " + token}
    client.post("/api/quest/quiz/submit", json={"quiz_id": "etfs-quiz", "score": 80}, headers=headers)
    resp2 = client.post("/api/quest/quiz/submit", json={"quiz_id": "etfs-quiz", "score": 80}, headers=headers)
    assert resp2.status_code == 200
    assert resp2.get_json()["xp_awarded"] == 0


def test_quest_quiz_submit_requires_auth(client):
    response = client.post("/api/quest/quiz/submit", json={"quiz_id": "any", "score": 70})
    assert response.status_code == 401


def test_quest_quiz_submit_requires_quiz_id(client):
    token = _register_and_login_quest(client, "quizuser4@example.com")
    response = client.post(
        "/api/quest/quiz/submit",
        json={"score": 80},
        headers={"Authorization": "Bearer " + token},
    )
    assert response.status_code == 400


def test_quest_challenge_awards_first_steps_badge(client):
    """Reaching 10 XP for the first time should award 'First Steps' badge."""
    token = _register_and_login_quest(client, "badgeuser1@example.com")
    headers = {"Authorization": "Bearer " + token}
    response = client.post(
        "/api/quest/challenge/submit",
        json={"challenge_id": "badge-test-1", "xp_reward": 10},
        headers=headers,
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert "First Steps" in payload["new_badges"]
    # Badge should also appear in profile
    badge_names = [b["name"] for b in payload["profile"]["badges"]]
    assert "First Steps" in badge_names


def test_quest_challenge_badge_only_awarded_once(client):
    """Second submission that crosses the same threshold does NOT re-award the badge."""
    token = _register_and_login_quest(client, "badgeuser2@example.com")
    headers = {"Authorization": "Bearer " + token}
    # Earn enough XP for 'First Steps' (10 XP)
    client.post("/api/quest/challenge/submit", json={"challenge_id": "b2-ch1", "xp_reward": 10}, headers=headers)
    # Earn more XP via a new challenge
    resp2 = client.post("/api/quest/challenge/submit", json={"challenge_id": "b2-ch2", "xp_reward": 5}, headers=headers)
    assert resp2.status_code == 200
    # 'First Steps' should NOT appear in new_badges again
    assert "First Steps" not in resp2.get_json()["new_badges"]


def test_quest_list_challenges_returns_catalogue(client):
    response = client.get("/api/quest/challenges")
    assert response.status_code == 200
    challenges = response.get_json()["challenges"]
    assert len(challenges) >= 5
    ids = [c["id"] for c in challenges]
    assert "investing-basics-quiz" in ids
    assert "diversification-quiz" in ids


def test_quest_profile_includes_badge_earned_at(client):
    """Badge serialization includes earned_at timestamp in Phase 3."""
    token = _register_and_login_quest(client, "badgetime@example.com")
    headers = {"Authorization": "Bearer " + token}
    client.post("/api/quest/challenge/submit", json={"challenge_id": "time-test", "xp_reward": 15}, headers=headers)
    profile = client.get("/api/quest/profile", headers=headers).get_json()
    badges = profile["badges"]
    assert len(badges) > 0
    assert "earned_at" in badges[0]


# ---------------------------------------------------------------------------
# Subscription / Entitlements
# ---------------------------------------------------------------------------

def test_account_plan_requires_auth(client):
    response = client.get("/api/account/plan")
    assert response.status_code == 401


def test_account_plan_defaults_to_free(client):
    """New users without a subscription record are on the Free plan."""
    client.post(
        "/api/auth/register",
        json={"email": "freeplan@example.com", "password": "Pass1234!", "full_name": "Free User"},
    )
    resp = client.post("/api/auth/login", json={"email": "freeplan@example.com", "password": "Pass1234!"})
    token = resp.get_json()["token"]
    response = client.get("/api/account/plan", headers={"Authorization": "Bearer " + token})
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["plan_id"] == "free"
    assert "ai_assistant_basic" in payload["features"]
    # Free users don't get extended features
    assert "portfolio_analytics_full" not in payload["features"]


# ---------------------------------------------------------------------------
# Entitlement unit tests (no HTTP needed)
# ---------------------------------------------------------------------------

def test_has_feature_free_plan_basic_ai(app):
    from backend.app.core.entitlements import Feature, _PLAN_FEATURES
    with app.app_context():
        assert Feature.AI_ASSISTANT_BASIC in _PLAN_FEATURES["free"]
        assert Feature.AI_ASSISTANT_EXTENDED not in _PLAN_FEATURES["free"]
        assert Feature.PORTFOLIO_ANALYTICS_FULL not in _PLAN_FEATURES["free"]


def test_has_feature_single_plan_includes_analytics(app):
    from backend.app.core.entitlements import Feature, _PLAN_FEATURES
    with app.app_context():
        assert Feature.PORTFOLIO_ANALYTICS_FULL in _PLAN_FEATURES["single"]
        assert Feature.CHART_DATA in _PLAN_FEATURES["single"]
        assert Feature.WATCHLIST in _PLAN_FEATURES["single"]


def test_has_feature_business_plan_has_team_dashboard(app):
    from backend.app.core.entitlements import Feature, _PLAN_FEATURES
    with app.app_context():
        assert Feature.TEAM_DASHBOARD in _PLAN_FEATURES["business"]
        assert Feature.FAMILY_PROFILES in _PLAN_FEATURES["business"]
