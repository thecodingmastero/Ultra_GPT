from __future__ import annotations


def test_register_login_and_me(client):
    register_response = client.post(
        "/api/auth/register",
        json={"full_name": "Ada Investor", "email": "ada@example.com", "password": "secret123"},
    )
    assert register_response.status_code == 201
    register_payload = register_response.get_json()
    assert register_payload["user"]["email"] == "ada@example.com"

    login_response = client.post(
        "/api/auth/login",
        json={"email": "ada@example.com", "password": "secret123"},
    )
    assert login_response.status_code == 200
    token = login_response.get_json()["token"]

    me_response = client.get("/api/account/me", headers={"Authorization": "Bearer " + token})
    assert me_response.status_code == 200
    assert me_response.get_json()["full_name"] == "Ada Investor"

    update_response = client.put(
        "/api/account/me",
        json={"full_name": "Ada Long Term"},
        headers={"Authorization": "Bearer " + token},
    )
    assert update_response.status_code == 200
    assert update_response.get_json()["full_name"] == "Ada Long Term"

    logout_response = client.post("/api/auth/logout")
    assert logout_response.status_code == 200
    assert logout_response.get_json()["logged_out"] is True
