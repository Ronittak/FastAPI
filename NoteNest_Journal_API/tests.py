from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_create_notebook():
    response = client.post(
        "/notebooks",
        json={
            "title": "Morning Pages",
            "author": "Riya Kapoor"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert "id" in data
    assert data["title"] == "Morning Pages"
    assert data["author"] == "Riya Kapoor"


def test_create_notebook_empty_title():
    response = client.post(
        "/notebooks",
        json={
            "title": "",
            "author": "Riya Kapoor"
        }
    )

    assert response.status_code == 422


def test_add_entry():
    notebook_response = client.post(
        "/notebooks",
        json={
            "title": "Morning Pages",
            "author": "Riya Kapoor"
        }
    )

    notebook_id = notebook_response.json()["id"]

    response = client.post(
        f"/notebooks/{notebook_id}/entries",
        json={
            "heading": "First Light",
            "mood": "calm",
            "word_count": 180
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert "id" in data
    assert data["heading"] == "First Light"
    assert data["mood"] == "calm"
    assert data["word_count"] == 180


def test_get_notebook():
    notebook_response = client.post(
        "/notebooks",
        json={
            "title": "Morning Pages",
            "author": "Riya Kapoor"
        }
    )

    notebook_id = notebook_response.json()["id"]

    client.post(
        f"/notebooks/{notebook_id}/entries",
        json={
            "heading": "First Light",
            "mood": "calm",
            "word_count": 180
        }
    )

    response = client.get(f"/notebooks/{notebook_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == notebook_id
    assert data["title"] == "Morning Pages"
    assert data["author"] == "Riya Kapoor"

    assert len(data["entries"]) == 1

    assert data["entries"][0]["heading"] == "First Light"
    assert data["entries"][0]["mood"] == "calm"
    assert data["entries"][0]["word_count"] == 180


def test_get_notebook_with_filter_and_sort():
    notebook_response = client.post(
        "/notebooks",
        json={
            "title": "Morning Pages",
            "author": "Riya Kapoor"
        }
    )

    notebook_id = notebook_response.json()["id"]

    client.post(
        f"/notebooks/{notebook_id}/entries",
        json={
            "heading": "First Light",
            "mood": "calm",
            "word_count": 300
        }
    )

    client.post(
        f"/notebooks/{notebook_id}/entries",
        json={
            "heading": "Quiet Morning",
            "mood": "happy",
            "word_count": 100
        }
    )

    client.post(
        f"/notebooks/{notebook_id}/entries",
        json={
            "heading": "Soft Rain",
            "mood": "calm",
            "word_count": 150
        }
    )

    response = client.get(
        f"/notebooks/{notebook_id}?mood=calm&sort=word_count"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == notebook_id
    assert data["title"] == "Morning Pages"
    assert data["author"] == "Riya Kapoor"

    assert len(data["entries"]) == 2

    assert all(
        entry["mood"] == "calm"
        for entry in data["entries"]
    )

    assert data["entries"][0]["word_count"] == 150
    assert data["entries"][1]["word_count"] == 300


def test_clear_entries():
    notebook_response = client.post(
        "/notebooks",
        json={
            "title": "Morning Pages",
            "author": "Riya Kapoor"
        }
    )

    notebook_id = notebook_response.json()["id"]

    client.post(
        f"/notebooks/{notebook_id}/entries",
        json={
            "heading": "First Light",
            "mood": "calm",
            "word_count": 180
        }
    )

    client.post(
        f"/notebooks/{notebook_id}/entries",
        json={
            "heading": "Second Entry",
            "mood": "happy",
            "word_count": 200
        }
    )

    response = client.delete(
        f"/notebooks/{notebook_id}/entries"
    )

    assert response.status_code == 204
    assert response.content == b""

    response = client.get(
        f"/notebooks/{notebook_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == notebook_id
    assert data["title"] == "Morning Pages"
    assert data["author"] == "Riya Kapoor"

    assert data["entries"] == []


def test_get_nonexistent_notebook():
    response = client.get("/notebooks/999999")

    assert response.status_code == 404


def test_delete_entries_nonexistent_notebook():
    response = client.delete("/notebooks/999999/entries")

    assert response.status_code == 404


def test_invalid_sort():
    notebook_response = client.post(
        "/notebooks",
        json={
            "title": "Morning Pages",
            "author": "Riya Kapoor"
        }
    )

    notebook_id = notebook_response.json()["id"]

    response = client.get(
        f"/notebooks/{notebook_id}?sort=author"
    )

    assert response.status_code == 422