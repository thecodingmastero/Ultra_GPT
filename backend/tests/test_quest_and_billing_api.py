from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Billing
# ---------------------------------------------------------------------------

def test_billing_plans_returns_all_four_tiers(client):
    response = client.get("/api/billing/plans")
    assert response.status_code == 200

    payload = response.get_json()
    assert "plans" in payload
    plan_names = [p["name"] for p in payload["plans"]]
    assert "Free" in plan_names
    assert "Single" in plan_names
    assert "Family" in plan_names
    assert "Business" in plan_names


def test_billing_single_plan_costs_ten_dollars(client):
    response = client.get("/api/billing/plans")
    plans = {p["id"]: p for p in response.get_json()["plans"]}
    assert plans["single"]["price_monthly"] == 10.0


def test_billing_free_plan_is_zero_cost(client):
    response = client.get("/api/billing/plans")
    plans = {p["id"]: p for p in response.get_json()["plans"]}
    assert plans["free"]["price_monthly"] == 0.0


# ---------------------------------------------------------------------------
# Quest
# ---------------------------------------------------------------------------

def _register_and_login(client) -> str:
    client.post(
        "/api/auth/register",
        json={"email": "questuser@example.com", "password": "Pass1234!", "full_name": "Quest User"},
    )
    resp = client.post(
        "/api/auth/login",
        json={"email": "questuser@example.com", "password": "Pass1234!"},
    )
    return resp.get_json()["token"]


def test_quest_profile_requires_auth(client):
    response = client.get("/api/quest/profile")
    assert response.status_code == 401


def test_quest_profile_creates_profile_on_first_access(client):
    token = _register_and_login(client)
    response = client.get("/api/quest/profile", headers={"Authorization": "Bearer " + token})
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["level"] == 1
    assert payload["xp"] == 0
    assert payload["badges"] == []


def test_quest_challenge_submit_requires_auth(client):
    response = client.post("/api/quest/challenge/submit", json={"challenge_id": "quiz-1"})
    assert response.status_code == 401


def test_quest_challenge_submit_awards_xp(client):
    token = _register_and_login(client)
    headers = {"Authorization": "Bearer " + token}
    response = client.post(
        "/api/quest/challenge/submit",
        json={"challenge_id": "quiz-1", "xp_reward": 20},
        headers=headers,
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["xp_awarded"] == 20
    assert payload["profile"]["xp"] == 20


def test_quest_challenge_submit_idempotent(client):
    token = _register_and_login(client)
    headers = {"Authorization": "Bearer " + token}
    client.post(
        "/api/quest/challenge/submit",
        json={"challenge_id": "quiz-idempotent", "xp_reward": 10},
        headers=headers,
    )
    resp2 = client.post(
        "/api/quest/challenge/submit",
        json={"challenge_id": "quiz-idempotent", "xp_reward": 10},
        headers=headers,
    )
    assert resp2.status_code == 200
    assert resp2.get_json()["xp_awarded"] == 0


def test_quest_challenge_submit_requires_challenge_id(client):
    token = _register_and_login(client)
    response = client.post(
        "/api/quest/challenge/submit",
        json={},
        headers={"Authorization": "Bearer " + token},
    )
    assert response.status_code == 400


def test_assistant_chat_does_not_award_quest_xp(client):
    token = _register_and_login(client)
    headers = {"Authorization": "Bearer " + token}

    profile_before = client.get("/api/quest/profile", headers=headers).get_json()
    assert profile_before["xp"] == 0

    assistant_response = client.post(
        "/api/assistant/chat",
        json={"message": "What is diversification?"},
        headers=headers,
    )
    assert assistant_response.status_code == 200
    assistant_payload = assistant_response.get_json()
    assert "response" in assistant_payload
    assert isinstance(assistant_payload["behavioral_signals"], list)

    profile_after = client.get("/api/quest/profile", headers=headers).get_json()
    assert profile_after["xp"] == 0


# ---------------------------------------------------------------------------
# Education routes
# ---------------------------------------------------------------------------

def test_education_lessons_returns_list(client):
    response = client.get("/api/education/lessons")
    assert response.status_code == 200
    assert "lessons" in response.get_json()


def test_education_progress_requires_auth(client):
    """Education progress endpoint now requires authentication (Phase 3 upgrade)."""
    response = client.post("/api/education/progress", json={"lesson_id": 1, "completed": True})
    assert response.status_code == 401


def test_education_progress_persists_for_authenticated_user(client):
    """Authenticated users can persist lesson progress via /api/education/progress."""
    # Seed lessons first by loading the list
    client.get("/api/education/lessons")

    client.post(
        "/api/auth/register",
        json={"email": "eduprogress@example.com", "password": "Pass1234!", "full_name": "Edu User"},
    )
    resp = client.post(
        "/api/auth/login",
        json={"email": "eduprogress@example.com", "password": "Pass1234!"},
    )
    token = resp.get_json()["token"]
    headers = {"Authorization": "Bearer " + token}

    response = client.post("/api/education/progress", json={"lesson_id": 1, "completed": True}, headers=headers)
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["lesson_id"] == 1
    assert payload["completed"] is True
    assert payload["message"] == "Progress recorded."


def test_education_progress_requires_lesson_id(client):
    """Missing lesson_id returns 401 (auth check happens before validation)."""
    response = client.post("/api/education/progress", json={})
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Market path-param endpoints
# ---------------------------------------------------------------------------

def test_market_quote_by_ticker_path_param(client):
    response = client.get("/api/market/quote/AAPL")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["symbol"] == "AAPL"


def test_market_chart_returns_ohlcv_candles(client):
    response = client.get("/api/market/chart/AAPL")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["symbol"] == "AAPL"
    assert "candles" in payload
    assert isinstance(payload["candles"], list)
    assert len(payload["candles"]) > 0
    assert "disclaimer" in payload


# ---------------------------------------------------------------------------
# Assistant /query alias
# ---------------------------------------------------------------------------

def test_assistant_query_alias_works(client):
    response = client.post(
        "/api/assistant/query",
        json={"message": "What is diversification?"},
    )
    assert response.status_code == 200
    assert "response" in response.get_json()


def test_assistant_query_requires_message(client):
    response = client.post("/api/assistant/query", json={})
    assert response.status_code == 400
