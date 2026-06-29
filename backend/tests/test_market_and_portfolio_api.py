from __future__ import annotations


def test_market_quote_returns_company_name_and_price(client):
    response = client.get("/api/market/quote?symbol=AAPL")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["company_name"] == "AAPL Incorporated"
    assert payload["current_price"] == 200.0


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
    assert payload["risk_flags"]
