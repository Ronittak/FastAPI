from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def create_lot(name="Terminal A Lot", zone="Airport"):
    response = client.post(
        "/lots",
        json={
            "name": name,
            "zone": zone
        }
    )
    return response


def add_slip(lot_id, ticket_code, vehicle_class, parked_minutes):
    return client.post(
        f"/lots/{lot_id}/slips",
        json={
            "ticket_code": ticket_code,
            "vehicle_class": vehicle_class,
            "parked_minutes": parked_minutes
        }
    )


# --------------------------------------------------
# 1. CREATE LOT
# --------------------------------------------------

def test_create_lot():
    response = create_lot()

    assert response.status_code == 201

    data = response.json()

    assert "id" in data
    assert data["name"] == "Terminal A Lot"
    assert data["zone"] == "Airport"


# --------------------------------------------------
# 2. CREATE LOT - EMPTY NAME
# --------------------------------------------------

def test_create_lot_empty_name():
    response = client.post(
        "/lots",
        json={
            "name": "",
            "zone": "Airport"
        }
    )

    assert response.status_code == 422


# --------------------------------------------------
# 3. ADD SLIP
# --------------------------------------------------

def test_add_slip():
    lot_response = create_lot()

    assert lot_response.status_code == 201

    lot_id = lot_response.json()["id"]

    response = add_slip(
        lot_id,
        "TK-001",
        "sedan",
        45
    )

    assert response.status_code == 201

    data = response.json()

    assert "id" in data
    assert data["ticket_code"] == "TK-001"
    assert data["vehicle_class"] == "sedan"
    assert data["parked_minutes"] == 45


# --------------------------------------------------
# 4. GET LOT WITH NESTED SLIPS
# --------------------------------------------------

def test_get_lot():
    lot_response = create_lot()

    lot_id = lot_response.json()["id"]

    add_slip(
        lot_id,
        "TK-001",
        "sedan",
        45
    )

    response = client.get(f"/lots/{lot_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == lot_id
    assert data["name"] == "Terminal A Lot"
    assert data["zone"] == "Airport"

    assert len(data["slips"]) == 1

    assert data["slips"][0]["ticket_code"] == "TK-001"
    assert data["slips"][0]["vehicle_class"] == "sedan"
    assert data["slips"][0]["parked_minutes"] == 45


# --------------------------------------------------
# 5. GET LOT - FILTER BY VEHICLE CLASS
# --------------------------------------------------

def test_get_lot_with_filter():
    lot_response = create_lot()

    lot_id = lot_response.json()["id"]

    add_slip(
        lot_id,
        "TK-001",
        "sedan",
        45
    )

    add_slip(
        lot_id,
        "TK-002",
        "suv",
        60
    )

    add_slip(
        lot_id,
        "TK-003",
        "sedan",
        30
    )

    response = client.get(
        f"/lots/{lot_id}?vehicle_class=sedan"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == lot_id
    assert data["name"] == "Terminal A Lot"
    assert data["zone"] == "Airport"

    assert len(data["slips"]) == 2

    assert all(
        slip["vehicle_class"] == "sedan"
        for slip in data["slips"]
    )


# --------------------------------------------------
# 6. GET LOT - FILTER + SORT
# --------------------------------------------------

def test_get_lot_with_filter_and_sort():
    lot_response = create_lot()

    lot_id = lot_response.json()["id"]

    add_slip(
        lot_id,
        "TK-001",
        "sedan",
        45
    )

    add_slip(
        lot_id,
        "TK-002",
        "suv",
        60
    )

    add_slip(
        lot_id,
        "TK-003",
        "sedan",
        30
    )

    add_slip(
        lot_id,
        "TK-004",
        "sedan",
        90
    )

    response = client.get(
        f"/lots/{lot_id}?vehicle_class=sedan&sort=parked_minutes"
    )

    assert response.status_code == 200

    data = response.json()

    # Lot fields remain unchanged
    assert data["id"] == lot_id
    assert data["name"] == "Terminal A Lot"
    assert data["zone"] == "Airport"

    # Only sedan slips
    assert len(data["slips"]) == 3

    assert all(
        slip["vehicle_class"] == "sedan"
        for slip in data["slips"]
    )

    # Ascending parked_minutes
    assert data["slips"][0]["parked_minutes"] == 30
    assert data["slips"][1]["parked_minutes"] == 45
    assert data["slips"][2]["parked_minutes"] == 90


# --------------------------------------------------
# 7. TRANSFER SLIPS
# --------------------------------------------------

def test_transfer_slips():
    source_response = create_lot(
        "Terminal A Lot",
        "Airport"
    )

    target_response = create_lot(
        "Terminal B Lot",
        "Airport"
    )

    source_id = source_response.json()["id"]
    target_id = target_response.json()["id"]

    add_slip(
        source_id,
        "TK-001",
        "sedan",
        45
    )

    response = client.post(
        f"/lots/{source_id}/slips/transfer",
        json={
            "target_lot_id": target_id
        }
    )

    assert response.status_code == 200

    data = response.json()

    # Receiving lot is returned
    assert data["id"] == target_id
    assert data["name"] == "Terminal B Lot"
    assert data["zone"] == "Airport"

    # Slip was transferred
    assert len(data["slips"]) == 1

    assert data["slips"][0]["ticket_code"] == "TK-001"
    assert data["slips"][0]["vehicle_class"] == "sedan"
    assert data["slips"][0]["parked_minutes"] == 45


# --------------------------------------------------
# 8. SOURCE LOT IS EMPTY AFTER TRANSFER
# --------------------------------------------------

def test_source_lot_empty_after_transfer():
    source_response = create_lot(
        "Terminal A Lot",
        "Airport"
    )

    target_response = create_lot(
        "Terminal B Lot",
        "Airport"
    )

    source_id = source_response.json()["id"]
    target_id = target_response.json()["id"]

    add_slip(
        source_id,
        "TK-001",
        "sedan",
        45
    )

    client.post(
        f"/lots/{source_id}/slips/transfer",
        json={
            "target_lot_id": target_id
        }
    )

    # Read source lot again
    response = client.get(
        f"/lots/{source_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == source_id
    assert data["slips"] == []


# --------------------------------------------------
# 9. TRANSFER MULTIPLE SLIPS
# --------------------------------------------------

def test_transfer_multiple_slips():
    source_response = create_lot(
        "Terminal A Lot",
        "Airport"
    )

    target_response = create_lot(
        "Terminal B Lot",
        "Airport"
    )

    source_id = source_response.json()["id"]
    target_id = target_response.json()["id"]

    add_slip(
        source_id,
        "TK-001",
        "sedan",
        45
    )

    add_slip(
        source_id,
        "TK-002",
        "suv",
        60
    )

    add_slip(
        source_id,
        "TK-003",
        "hatchback",
        30
    )

    response = client.post(
        f"/lots/{source_id}/slips/transfer",
        json={
            "target_lot_id": target_id
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == target_id
    assert len(data["slips"]) == 3

    ticket_codes = [
        slip["ticket_code"]
        for slip in data["slips"]
    ]

    assert "TK-001" in ticket_codes
    assert "TK-002" in ticket_codes
    assert "TK-003" in ticket_codes


# --------------------------------------------------
# 10. TRANSFER EMPTY QUEUE
# --------------------------------------------------

def test_transfer_empty_queue():
    source_response = create_lot(
        "Terminal A Lot",
        "Airport"
    )

    target_response = create_lot(
        "Terminal B Lot",
        "Airport"
    )

    source_id = source_response.json()["id"]
    target_id = target_response.json()["id"]

    response = client.post(
        f"/lots/{source_id}/slips/transfer",
        json={
            "target_lot_id": target_id
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == target_id
    assert data["name"] == "Terminal B Lot"
    assert data["zone"] == "Airport"
    assert data["slips"] == []


# --------------------------------------------------
# 11. GET NON-EXISTENT LOT
# --------------------------------------------------

def test_get_nonexistent_lot():
    response = client.get("/lots/999999")

    assert response.status_code == 404


# --------------------------------------------------
# 12. TRANSFER FROM NON-EXISTENT LOT
# --------------------------------------------------

def test_transfer_from_nonexistent_lot():
    target_response = create_lot(
        "Terminal B Lot",
        "Airport"
    )

    target_id = target_response.json()["id"]

    response = client.post(
        "/lots/999999/slips/transfer",
        json={
            "target_lot_id": target_id
        }
    )

    assert response.status_code == 404


# --------------------------------------------------
# 13. TRANSFER TO NON-EXISTENT LOT
# --------------------------------------------------

def test_transfer_to_nonexistent_lot():
    source_response = create_lot(
        "Terminal A Lot",
        "Airport"
    )

    source_id = source_response.json()["id"]

    add_slip(
        source_id,
        "TK-001",
        "sedan",
        45
    )

    response = client.post(
        f"/lots/{source_id}/slips/transfer",
        json={
            "target_lot_id": 999999
        }
    )

    assert response.status_code == 404

    # Make sure the slip was NOT moved
    response = client.get(
        f"/lots/{source_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["slips"]) == 1
    assert data["slips"][0]["ticket_code"] == "TK-001"


# --------------------------------------------------
# 14. INVALID SORT VALUE
# --------------------------------------------------

def test_invalid_sort():
    lot_response = create_lot()

    lot_id = lot_response.json()["id"]

    response = client.get(
        f"/lots/{lot_id}?sort=zone"
    )

    assert response.status_code == 422