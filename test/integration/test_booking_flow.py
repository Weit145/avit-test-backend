import requests
import time
import os
from datetime import date, datetime, timedelta, timezone

BASE_URL = os.environ.get("BASE_URL", "http://app:8000")


def get_token(role: str) -> str:
    resp = requests.post(f"{BASE_URL}/dummyLogin", json=role, timeout=5)
    return resp.json().get("jwt")


def wait_host(attempt: int = 10, sleeping: int = 5):
    for _ in range(attempt):
        try:
            requests.get(f"{BASE_URL}/_info")
            break
        except requests.ConnectionError:
            time.sleep(sleeping)
    else:
        raise ConnectionError("API did not become available.")


def create_room(token: str, data: dict = {}):
    if data == {}:
        data = {"name": "Test", "description": "Test", "capacity": 1}
    create_room_resp = requests.post(
        f"{BASE_URL}/rooms/create",
        json=data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create_room_resp.status_code == 201
    return create_room_resp.json()


def create_schedule(room_id: str, token: str, data: dict = {}):
    if data == {}:
        data = {
            "daysOfWeek": [1, 2, 3, 4, 5, 6, 7],
            "startTime": "10:00",
            "endTime": "11:00",
        }
    schedule_resp = requests.post(
        f"{BASE_URL}/rooms/{room_id}/schedule/create",
        json=data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert schedule_resp.status_code == 201
    return


def get_rooms(
    room_id: str,
    token: str,
    test_date: date = datetime.now(timezone.utc).date() + timedelta(days=1),
):
    slots_resp = requests.get(
        f"{BASE_URL}/rooms/{room_id}/slots/list",
        params={"date": test_date.isoformat()},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert slots_resp.status_code == 200
    slots = slots_resp.json()
    assert len(slots) > 0, "Нет слотов на выбранную дату"
    return slots


def create_booking(slot_id: str, token: str, data: dict = {}):
    if data == {}:
        data = {"slotId": slot_id, "conferenceLink": False}
    create_booking_resp = requests.post(
        f"{BASE_URL}/bookings/create",
        json=data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create_booking_resp.status_code == 201
    booking = create_booking_resp.json()
    booking_id = booking.get("id")
    assert booking["status"] == "active"
    return booking_id


def my_booking(booking_id: str, token: str):
    my_bookings_resp = requests.get(
        f"{BASE_URL}/bookings/my", headers={"Authorization": f"Bearer {token}"}
    )
    assert my_bookings_resp.status_code == 200
    my_bookings = my_bookings_resp.json()
    assert any(b.get("id") == booking_id for b in my_bookings)


def cancel_booking(booking_id: str, token: str):
    cancel_resp = requests.post(
        f"{BASE_URL}/bookings/{booking_id}/cancel",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert cancel_resp.status_code == 200
    cancel_resp2 = requests.post(
        f"{BASE_URL}/bookings/{booking_id}/cancel",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert cancel_resp2.status_code == 200


def test_full_booking_flow():

    wait_host()

    # Create room
    admin_token = get_token("admin")
    room = create_room(admin_token)
    room_id = room.get("id")

    # Create schedule
    create_schedule(room_id, admin_token)

    # Get rooms
    test_date = datetime.now(timezone.utc).date() + timedelta(days=1)
    slots = get_rooms(room_id, admin_token, test_date)
    slot_id = slots[0].get("id")

    # Create booking
    user_token = get_token("user")
    booking_id = create_booking(slot_id, user_token)

    # My bookings
    my_booking(booking_id, user_token)

    # Cancel booking
    cancel_booking(booking_id, user_token)


if __name__ == "__main__":
    test_full_booking_flow()
