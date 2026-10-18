def _create(client, **payload):
    return client.post("/api/tasks", json=payload)


def test_new_task_defaults_to_medium_priority(client):
    response = _create(client, title="Write report")
    assert response.status_code == 201
    assert response.get_json()["priority"] == "medium"


def test_task_keeps_the_priority_it_was_created_with(client):
    for priority in ("low", "medium", "high"):
        response = _create(client, title=f"{priority} task", priority=priority)
        assert response.status_code == 201
        assert response.get_json()["priority"] == priority


def test_invalid_priority_is_rejected(client):
    response = _create(client, title="Bad priority", priority="urgent")
    assert response.status_code == 400


def test_tasks_can_be_filtered_by_priority(client):
    _create(client, title="Fix outage", priority="high")
    _create(client, title="Tidy desk", priority="low")
    response = client.get("/api/tasks?priority=high")
    assert [task["title"] for task in response.get_json()] == ["Fix outage"]


def test_priority_can_be_updated(client):
    task_id = _create(client, title="Plan sprint").get_json()["id"]
    response = client.put(f"/api/tasks/{task_id}", json={"priority": "high"})
    assert response.status_code == 200
    assert response.get_json()["priority"] == "high"


def test_ui_form_creates_a_task_and_shows_its_priority(client):
    response = client.post(
        "/tasks", data={"title": "From the form", "priority": "high"}, follow_redirects=True
    )
    assert response.status_code == 200
    assert b"From the form" in response.data
    assert b'class="badge high"' in response.data


def test_health_and_ready_endpoints(client):
    assert client.get("/health").status_code == 200
    assert client.get("/ready").status_code == 200
