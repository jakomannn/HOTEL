import os
import time
from datetime import datetime, timedelta

import pytest
import requests


API_URL = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

MANAGER_EMAIL = os.getenv("MANAGER_EMAIL", ADMIN_EMAIL)
MANAGER_PASSWORD = os.getenv("MANAGER_PASSWORD", ADMIN_PASSWORD)


def require_env():
    missing = []

    if not ADMIN_EMAIL:
        missing.append("ADMIN_EMAIL")

    if not ADMIN_PASSWORD:
        missing.append("ADMIN_PASSWORD")

    if not MANAGER_EMAIL:
        missing.append("MANAGER_EMAIL")

    if not MANAGER_PASSWORD:
        missing.append("MANAGER_PASSWORD")

    if missing:
        pytest.skip(
            "Missing environment variables: " + ", ".join(missing)
        )


def request_json(
    method: str,
    path: str,
    token: str | None = None,
    expected_status: int | tuple[int, ...] = 200,
    **kwargs
):
    headers = kwargs.pop("headers", {})

    if token is not None:
        headers["Authorization"] = f"Bearer {token}"

    response = requests.request(
        method=method,
        url=f"{API_URL}{path}",
        headers=headers,
        timeout=15,
        **kwargs
    )

    allowed_statuses = (
        expected_status
        if isinstance(expected_status, tuple)
        else (expected_status,)
    )

    assert response.status_code in allowed_statuses, (
        f"{method} {path} failed\n"
        f"Expected: {allowed_statuses}\n"
        f"Actual: {response.status_code}\n"
        f"Response: {response.text}"
    )

    if response.text:
        return response.json()

    return None


def login(email: str, password: str) -> str:
    data = {
        "username": email,
        "password": password
    }

    response = request_json(
        "POST",
        "/auth/login",
        expected_status=200,
        data=data
    )

    assert "access_token" in response

    return response["access_token"]


def get_me(token: str) -> dict:
    return request_json(
        "GET",
        "/auth/me",
        token=token,
        expected_status=200
    )


@pytest.fixture(scope="session")
def admin_token():
    require_env()
    return login(ADMIN_EMAIL, ADMIN_PASSWORD)


@pytest.fixture(scope="session")
def manager_token():
    require_env()
    return login(MANAGER_EMAIL, MANAGER_PASSWORD)


@pytest.fixture(scope="session")
def manager_employee(manager_token):
    return get_me(manager_token)


def test_full_guest_reservation_payment_checkin_checkout_flow(
    admin_token,
    manager_token,
    manager_employee
):
    unique = int(time.time())

    category_payload = {
        "name": f"Test Category {unique}",
        "description": "Autotest room category",
        "max_guests": 2,
        "price_per_night": "100.00"
    }

    category = request_json(
        "POST",
        "/room-categories/",
        token=admin_token,
        expected_status=201,
        json=category_payload
    )

    assert category["category_id"] is not None
    assert category["price_per_night"] == "100.00"

    room_payload = {
        "room_number": unique,
        "category_id": category["category_id"],
        "status": "free"
    }

    room = request_json(
        "POST",
        "/rooms/",
        token=admin_token,
        expected_status=201,
        json=room_payload
    )

    assert room["room_id"] is not None
    assert room["status"] == "free"

    check_in_date = datetime.utcnow() + timedelta(days=1)
    check_out_date = check_in_date + timedelta(days=2)

    guest_payload = {
        "first_name": "Auto",
        "last_name": "Guest",
        "email": f"autoguest{unique}@example.com",
        "phone": f"+7999{unique}",
        "passport_number": f"AUTO{unique}",
        "room_id": room["room_id"],
        "check_in_date": check_in_date.isoformat(),
        "check_out_date": check_out_date.isoformat()
    }

    reservation_with_payment = request_json(
        "POST",
        "/reservations/guest",
        expected_status=201,
        json=guest_payload
    )

    reservation = reservation_with_payment["reservation"]
    payment = reservation_with_payment["payment"]

    assert reservation["reservation_id"] is not None
    assert reservation["status"] == "pending"

    assert payment["payment_id"] is not None
    assert payment["reservation_id"] == reservation["reservation_id"]
    assert payment["status"] == "pending"
    assert payment["amount"] == "200.00"

    paid_payment = request_json(
        "PATCH",
        f"/payments/{payment['payment_id']}/paid",
        expected_status=200
    )

    assert paid_payment["status"] == "paid"
    assert paid_payment["payment_date"] is not None

    confirmed_reservation = request_json(
        "GET",
        f"/reservations/{reservation['reservation_id']}",
        token=manager_token,
        expected_status=200
    )

    assert confirmed_reservation["status"] == "confirmed"

    check_in_payload = {
        "reservation_id": reservation["reservation_id"],
        "employee_id": manager_employee["employee_id"]
    }

    check_in = request_json(
        "POST",
        "/check-ins/",
        token=manager_token,
        expected_status=201,
        json=check_in_payload
    )

    assert check_in["check_in_id"] is not None
    assert check_in["reservation_id"] == reservation["reservation_id"]
    assert check_in["check_out_time"] is None

    occupied_room = request_json(
        "GET",
        f"/rooms/{room['room_id']}",
        token=manager_token,
        expected_status=200
    )

    assert occupied_room["status"] == "occupied"

    checked_out = request_json(
        "PATCH",
        f"/check-ins/{check_in['check_in_id']}/check-out",
        token=manager_token,
        expected_status=200,
        json={}
    )

    assert checked_out["check_out_time"] is not None

    completed_reservation = request_json(
        "GET",
        f"/reservations/{reservation['reservation_id']}",
        token=manager_token,
        expected_status=200
    )

    assert completed_reservation["status"] == "completed"

    cleaning_room = request_json(
        "GET",
        f"/rooms/{room['room_id']}",
        token=manager_token,
        expected_status=200
    )

    assert cleaning_room["status"] == "cleaning"

    stay_history = request_json(
        "GET",
        f"/stay-history/check-in/{check_in['check_in_id']}",
        token=manager_token,
        expected_status=200
    )

    assert stay_history["history_id"] is not None
    assert stay_history["reservation_id"] == reservation["reservation_id"]
    assert stay_history["check_in_id"] == check_in["check_in_id"]
    assert stay_history["client_id"] == reservation["client_id"]
    assert stay_history["room_id"] == room["room_id"]
    assert stay_history["total_nights"] >= 1
    assert stay_history["total_cost"] is not None


def test_audit_logs_created_for_admin_actions(admin_token):
    unique = int(time.time())

    category_payload = {
        "name": f"Audit Category {unique}",
        "description": "Audit autotest category",
        "max_guests": 2,
        "price_per_night": "150.00"
    }

    category = request_json(
        "POST",
        "/room-categories/",
        token=admin_token,
        expected_status=201,
        json=category_payload
    )

    logs = request_json(
        "GET",
        "/audit-logs/?table_name=room_categories&action_type=INSERT&limit=20",
        token=admin_token,
        expected_status=200
    )

    assert isinstance(logs, list)

    matching_logs = [
        log
        for log in logs
        if log["record_id"] == str(category["category_id"])
        and log["table_name"] == "room_categories"
        and log["action_type"] == "INSERT"
    ]

    assert matching_logs, "Audit log for room category INSERT was not found"