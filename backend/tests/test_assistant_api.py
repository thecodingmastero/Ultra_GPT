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


def test_assistant_uses_provider_for_educational_questions(client):
    response = client.post(
        "/api/assistant/chat",
        json={"message": "How does diversification reduce risk?"},
    )

    assert response.status_code == 200
    assert "diversification" in response.get_json()["response"].lower()
