from __future__ import annotations


def _register_and_login(client, email: str = "watchlist@example.com") -> str:
    client.post(
        "/api/auth/register",
        json={"email": email, "password": "Pass1234!", "full_name": "Watchlist User"},
    )
    resp = client.post("/api/auth/login", json={"email": email, "password": "Pass1234!"})
    return resp.get_json()["token"]


def test_watchlist_items_crud(client):
    token = _register_and_login(client)
    headers = {"Authorization": "Bearer " + token}

    create_response = client.post("/api/watchlist/items", json={"symbol": "AAPL"}, headers=headers)
    assert create_response.status_code == 201
    assert create_response.get_json()["created"] is True

    duplicate_response = client.post("/api/watchlist/items", json={"symbol": "AAPL"}, headers=headers)
    assert duplicate_response.status_code == 200
    assert duplicate_response.get_json()["created"] is False

    list_response = client.get("/api/watchlist/items", headers=headers)
    assert list_response.status_code == 200
    payload = list_response.get_json()
    assert len(payload["items"]) == 1
    assert payload["items"][0]["symbol"] == "AAPL"

    item_id = payload["items"][0]["id"]
    delete_response = client.delete(f"/api/watchlist/items/{item_id}", headers=headers)
    assert delete_response.status_code == 200
    assert delete_response.get_json()["deleted"] is True


def test_account_me_includes_watchlist_and_achievement_counters(client):
    token = _register_and_login(client, email="accountstats@example.com")
    headers = {"Authorization": "Bearer " + token}

    client.post("/api/watchlist/items", json={"symbol": "VOO"}, headers=headers)
    account_response = client.get("/api/account/me", headers=headers)
    assert account_response.status_code == 200
    payload = account_response.get_json()
    assert payload["watchlists"] == 1
    assert payload["watchlist_items"] == 1
    assert payload["achievements"] == 0
