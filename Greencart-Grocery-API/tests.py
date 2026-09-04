from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_create_store():
    response = client.post(
        "/stores",
        json={
            "name": "Fresh Corner",
            "city": "Pune"
        }
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "name": "Fresh Corner",
        "city": "Pune"
    }


def test_add_item():
    response = client.post(
        "/stores/1/items",
        json={
            "name": "Organic Tomatoes",
            "category": "produce",
            "stock_qty": 40
        }
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "name": "Organic Tomatoes",
        "category": "produce",
        "stock_qty": 40
    }


def test_get_store():
    response = client.get("/stores/1")

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "name": "Fresh Corner",
        "city": "Pune",
        "items": [
            {
                "id": 1,
                "name": "Organic Tomatoes",
                "category": "produce",
                "stock_qty": 40
            }
        ]
    }


def test_get_store_with_filter_and_sort():
    response = client.get(
        "/stores/1?category=produce&sort=stock_qty"
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "name": "Fresh Corner",
        "city": "Pune",
        "items": [
            {
                "id": 1,
                "name": "Organic Tomatoes",
                "category": "produce",
                "stock_qty": 40
            }
        ]
    }


def test_delete_item():
    response = client.delete("/stores/1/items/1")

    assert response.status_code == 204
    assert response.content == b""


def test_nonexistent_store():
    response = client.get("/stores/999")

    assert response.status_code == 404


def test_delete_item_from_wrong_store():
    response = client.delete("/stores/2/items/1")

    assert response.status_code == 404


def test_empty_store_name():
    response = client.post(
        "/stores",
        json={
            "name": "",
            "city": "Pune"
        }
    )

    assert response.status_code == 422


def test_invalid_sort():
    response = client.get("/stores/1?sort=city")

    assert response.status_code == 422