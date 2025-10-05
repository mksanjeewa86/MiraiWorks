from datetime import datetime, timedelta, timezone

import pytest


@pytest.mark.asyncio
async def test_todo_crud_flow(client, auth_headers):
    # Create todo
    payload = {
        "title": "Prepare onboarding",
        "description": "Collect documents for new hire",
        "due_date": (datetime.now(timezone.utc) + timedelta(days=3)).isoformat(),
    }
    create_resp = await client.post("/api/todos", json=payload, headers=auth_headers)
    assert create_resp.status_code == 201
    created = create_resp.json()

    todo_id = created["id"]
    assert created["status"] == "pending"

    # Update todo
    update_resp = await client.put(
        f"/api/todos/{todo_id}",
        json={"notes": "Remember to check references"},
        headers=auth_headers,
    )
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert updated["notes"] == "Remember to check references"

    # Complete todo
    complete_resp = await client.post(
        f"/api/todos/{todo_id}/complete", headers=auth_headers
    )
    assert complete_resp.status_code == 200
    assert complete_resp.json()["status"] == "completed"
    assert complete_resp.json()["completed_at"] is not None

    # Reopen todo
    reopen_resp = await client.post(
        f"/api/todos/{todo_id}/reopen", headers=auth_headers
    )
    assert reopen_resp.status_code == 200
    reopened = reopen_resp.json()
    assert reopened["status"] == "pending"

    # Recent endpoint should include todo
    recent_resp = await client.get("/api/todos/recent", headers=auth_headers)
    assert recent_resp.status_code == 200
    recent_items = recent_resp.json()
    assert any(item["id"] == todo_id for item in recent_items)

    # Delete todo
    delete_resp = await client.delete(f"/api/todos/{todo_id}", headers=auth_headers)
    assert delete_resp.status_code == 204

    # Ensure it no longer appears
    list_resp = await client.get("/api/todos", headers=auth_headers)
    assert list_resp.status_code == 200
    data = list_resp.json()
    assert all(item["id"] != todo_id for item in data["items"])


@pytest.mark.asyncio
async def test_overdue_todos_mark_expired(client, auth_headers):
    past_due_payload = {
        "title": "Submit expense report",
        "due_date": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
    }
    create_resp = await client.post(
        "/api/todos", json=past_due_payload, headers=auth_headers
    )
    assert create_resp.status_code == 201

    list_resp = await client.get("/api/todos", headers=auth_headers)
    assert list_resp.status_code == 200
    todos = list_resp.json()["items"]
    assert any(todo["status"] == "expired" for todo in todos)
