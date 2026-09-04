
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_create_depot():
    response = client.post(
        "/depots",
        json={
            "name": "Central Depot",
            "region": "Karnataka"
        }
    )

    assert response.status_code == 201

    assert response.json() == {
        "id": 1,
        "name": "Central Depot",
        "region": "Karnataka"
    }


def test_add_vehicle():
    response = client.post(
        "/depots/1/vehicles",
        json={
            "plate_number": "KA-05-AB-1234",
            "vehicle_type": "truck",
            "mileage": 12000
        }
    )

    assert response.status_code == 201

    assert response.json() == {
        "id": 1,
        "plate_number": "KA-05-AB-1234",
        "vehicle_type": "truck",
        "mileage": 12000
    }


def test_get_depot():
    response = client.get("/depots/1")

    assert response.status_code == 200

    assert response.json() == {
        "id": 1,
        "name": "Central Depot",
        "region": "Karnataka",
        "vehicles": [
            {
                "id": 1,
                "plate_number": "KA-05-AB-1234",
                "vehicle_type": "truck",
                "mileage": 12000
            }
        ]
    }


def test_get_depot_with_filter_and_sort():
    response = client.get(
        "/depots/1?vehicle_type=truck&sort=mileage"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert data["name"] == "Central Depot"
    assert data["region"] == "Karnataka"

    assert data["vehicles"] == [
        {
            "id": 1,
            "plate_number": "KA-05-AB-1234",
            "vehicle_type": "truck",
            "mileage": 12000
        }
    ]


def test_update_vehicle():
    response = client.put(
        "/depots/1/vehicles/1",
        json={
            "plate_number": "KA-05-AB-1234",
            "vehicle_type": "truck",
            "mileage": 18500
        }
    )

    assert response.status_code == 200

    assert response.json() == {
        "id": 1,
        "plate_number": "KA-05-AB-1234",
        "vehicle_type": "truck",
        "mileage": 18500
    }


def test_nonexistent_depot():
    response = client.get("/depots/999")

    assert response.status_code == 404


def test_vehicle_belongs_to_wrong_depot():
    response = client.put(
        "/depots/2/vehicles/1",
        json={
            "plate_number": "KA-05-AB-1234",
            "vehicle_type": "truck",
            "mileage": 18500
        }
    )

    assert response.status_code == 404







