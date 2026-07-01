from __future__ import annotations


def test_assistant_blocks_direct_buy_sell_requests(client):
    response = client.post("/api/assistant/chat", json={"message": "Should I buy Nvidia today?"})

    assert response.status_code == 200
    payload = response.get_json()
    assert "can’t give direct buy or sell instructions" in payload["response"]
    assert "education only" in payload["disclaimer"].lower()


def test_assistant_uses_provider_for_educational_questions(client):
    response = client.post(
        "/api/assistant/chat",
        json={"message": "How does diversification reduce risk?"},
    )

    assert response.status_code == 200
    assert "diversification" in response.get_json()["response"].lower()
