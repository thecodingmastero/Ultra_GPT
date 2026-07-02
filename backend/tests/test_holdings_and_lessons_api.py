from __future__ import annotations


def _auth_headers(client):
    register_response = client.post(
        "/api/auth/register",
        json={"full_name": "Holdings User", "email": "holdings@example.com", "password": "secret123"},
    )
    token = register_response.get_json()["token"]
    return {"Authorization": "Bearer " + token}


def test_holdings_crud_and_concentration_analysis(client):
    headers = _auth_headers(client)

    create_response = client.post("/api/holdings", json={"symbol": "AAPL", "quantity": 2}, headers=headers)
    assert create_response.status_code == 201
    holding_id = create_response.get_json()["id"]

    update_response = client.put(f"/api/holdings/{holding_id}", json={"symbol": "MSFT", "quantity": 3}, headers=headers)
    assert update_response.status_code == 200
    assert update_response.get_json()["symbol"] == "MSFT"

    list_response = client.get("/api/holdings", headers=headers)
    assert list_response.status_code == 200
    assert len(list_response.get_json()["holdings"]) == 1

    concentration_response = client.get("/api/portfolio/concentration", headers=headers)
    assert concentration_response.status_code == 200
    payload = concentration_response.get_json()
    assert payload["summary"]["position_count"] == 1
    assert payload["sector_breakdown"]
    assert payload["risk_flags"]

    delete_response = client.delete(f"/api/holdings/{holding_id}", headers=headers)
    assert delete_response.status_code == 200
    assert delete_response.get_json()["deleted"] is True


def test_lessons_listing_detail_and_progress_tracking(client):
    headers = _auth_headers(client)

    lessons_response = client.get("/api/lessons")
    assert lessons_response.status_code == 200
    lessons = lessons_response.get_json()["lessons"]
    assert lessons

    first_lesson_id = lessons[0]["id"]
    detail_response = client.get(f"/api/lessons/{first_lesson_id}")
    assert detail_response.status_code == 200
    assert detail_response.get_json()["content"]

    progress_response = client.post(f"/api/lessons/{first_lesson_id}/progress", json={"completed": True}, headers=headers)
    assert progress_response.status_code == 200
    assert progress_response.get_json()["completed"] is True

    progress_list_response = client.get("/api/lessons/progress", headers=headers)
    assert progress_list_response.status_code == 200
    assert first_lesson_id in progress_list_response.get_json()["completed_lesson_ids"]
