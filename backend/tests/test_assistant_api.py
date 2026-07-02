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
