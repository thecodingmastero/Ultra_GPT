from __future__ import annotations


def test_assistant_blocks_direct_buy_sell_requests(client):
    response = client.post("/api/assistant/chat", json={"message": "Should I buy Nvidia today?"})

    assert response.status_code == 200
    payload = response.get_json()
    assert "can’t provide direct buy/sell instructions" in payload["response"]
    assert "educational purposes only" in payload["disclaimer"].lower()


def test_assistant_blocks_guaranteed_return_prompts(client):
    response = client.post("/api/assistant/chat", json={"message": "Can you guarantee a sure profit if I buy this stock?"})

    assert response.status_code == 200
    assert "guaranteed-return claims" in response.get_json()["response"]


def test_assistant_blocks_directive_patterns_like_all_in(client):
    response = client.post("/api/assistant/chat", json={"message": "Should I go all in on one hot stock for a sure profit?"})

    assert response.status_code == 200
    payload = response.get_json()
    assert "can’t provide direct buy/sell instructions" in payload["response"]
    assert "lack_of_diversification" in payload["behavioral_signals"]
    assert "chasing_hot_stocks" in payload["behavioral_signals"]


def test_assistant_uses_provider_for_educational_questions(client):
    response = client.post(
        "/api/assistant/chat",
        json={"message": "How does diversification reduce risk?"},
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert "diversification" in payload["response"].lower()
    assert payload["behavioral_signals"] == []


def test_assistant_detects_behavioral_signals(client):
    response = client.post(
        "/api/assistant/chat",
        json={"message": "I have FOMO and feel this is easy money that can't lose."},
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert "fomo" in payload["behavioral_signals"]
    assert "overconfidence" in payload["behavioral_signals"]


# ---------------------------------------------------------------------------
# Phase 3 tests
# ---------------------------------------------------------------------------

def test_chat_returns_policy_metadata(client):
    """Response always includes policy_metadata with depth and blocked flag."""
    response = client.post(
        "/api/assistant/chat",
        json={"message": "What is dollar-cost averaging?"},
    )

    assert response.status_code == 200
    payload = response.get_json()
    meta = payload.get("policy_metadata")
    assert meta is not None
    assert meta["blocked"] is False
    assert meta["depth"] == "simple"


def test_chat_deep_depth_returns_correct_metadata(client):
    """Passing depth=deep is accepted and reflected in policy_metadata."""
    response = client.post(
        "/api/assistant/chat",
        json={"message": "Explain efficient market hypothesis in detail.", "depth": "deep"},
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["policy_metadata"]["depth"] == "deep"
    assert payload["policy_metadata"]["blocked"] is False


def test_chat_invalid_depth_returns_400(client):
    """An unrecognised depth value is rejected with HTTP 400."""
    response = client.post(
        "/api/assistant/chat",
        json={"message": "Tell me about ETFs.", "depth": "expert"},
    )

    assert response.status_code == 400
    assert "depth" in response.get_json()["error"].lower()


def test_chat_blocked_response_includes_policy_metadata(client):
    """Blocked responses set blocked=True in policy_metadata."""
    response = client.post(
        "/api/assistant/chat",
        json={"message": "Should I sell everything right now?"},
    )

    assert response.status_code == 200
    payload = response.get_json()
    meta = payload["policy_metadata"]
    assert meta["blocked"] is True
    assert meta["block_reason"] is not None


def test_chat_returns_behavioral_coaching_details(client):
    """behavioral_coaching field contains signal, confidence, and coaching text."""
    response = client.post(
        "/api/assistant/chat",
        json={"message": "I have FOMO and everyone is buying this hot stock to the moon."},
    )

    assert response.status_code == 200
    payload = response.get_json()
    coaching_list = payload.get("behavioral_coaching", [])
    assert isinstance(coaching_list, list)
    # At least one coaching entry expected
    assert len(coaching_list) > 0
    entry = coaching_list[0]
    assert "signal" in entry
    assert "confidence" in entry
    assert "coaching" in entry
    assert 0.0 <= entry["confidence"] <= 1.0


def test_behavioral_analyze_endpoint_returns_signals(client):
    """/api/assistant/behavioral/analyze returns structured coaching analysis."""
    response = client.post(
        "/api/assistant/behavioral/analyze",
        json={"message": "I have FOMO and want to go all in on a meme stock to the moon."},
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["analyzed"] is True
    assert isinstance(payload["signals"], list)
    assert isinstance(payload["signal_names"], list)
    assert len(payload["signals"]) > 0
    for sig in payload["signals"]:
        assert "signal" in sig
        assert "confidence" in sig
        assert "coaching" in sig
        assert 0.0 <= sig["confidence"] <= 1.0


def test_behavioral_analyze_returns_empty_for_neutral_text(client):
    """Neutral questions should not trigger any behavioral signals."""
    response = client.post(
        "/api/assistant/behavioral/analyze",
        json={"message": "What is an index fund?"},
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["analyzed"] is False
    assert payload["signals"] == []
    assert payload["signal_names"] == []


def test_behavioral_analyze_requires_message(client):
    """Missing message returns HTTP 400."""
    response = client.post("/api/assistant/behavioral/analyze", json={})

    assert response.status_code == 400


def test_chat_missing_message_returns_400(client):
    """Empty message returns HTTP 400."""
    response = client.post("/api/assistant/chat", json={"message": ""})

    assert response.status_code == 400


def test_behavioral_coaching_confidence_boost_on_multiple_matches(client):
    """Repeated signals in text should receive confidence bonus."""
    response = client.post(
        "/api/assistant/behavioral/analyze",
        json={"message": "FOMO FOMO everyone is buying and missing out, buy before it is too late!"},
    )

    assert response.status_code == 200
    payload = response.get_json()
    fomo_signals = [s for s in payload["signals"] if s["signal"] == "fomo"]
    assert len(fomo_signals) == 1
    # Multiple matches should push confidence above base of 0.80
    assert fomo_signals[0]["confidence"] >= 0.80
