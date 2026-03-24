import requests
import time
import os
from datetime import datetime, timedelta, timezone

BASE_URL = os.environ.get("BASE_URL", "http://app:8000") 

def get_token(role: str) -> str:
    resp = requests.post(f"{BASE_URL}/dummyLogin", json=role, timeout=5)
    return resp.json().get("jwt")
        


def test_full_booking_flow():
    for _ in range(10):
        try:
            requests.get(f"{BASE_URL}/_info")
            break
        except requests.ConnectionError:
            time.sleep(5)
    else:
        raise ConnectionError("API did not become available.")

    admin_token = get_token("admin")
    room_data = {
        "name": "Integration Test Room",
        "description": "Test",
        "capacity": 1
    }
    create_room_resp = requests.post(
        f"{BASE_URL}/rooms/create",
        json=room_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert create_room_resp.status_code == 201
    room = create_room_resp.json()
    room_id = room.get("id")


    schedule_data = {
        "daysOfWeek": [1, 2, 3, 4, 5, 6, 7],
        "startTime": "10:00",
        "endTime": "11:00"
    }
    schedule_resp = requests.post(
        f"{BASE_URL}/rooms/{room_id}/schedule/create",
        json=schedule_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert schedule_resp.status_code == 201

    test_date = datetime.now(timezone.utc).date() + timedelta(days=1)

    slots_resp = requests.get(
        f"{BASE_URL}/rooms/{room_id}/slots/list",
        params={"date": test_date.isoformat()},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert slots_resp.status_code == 200
    slots = slots_resp.json()
    assert len(slots) > 0, "Нет слотов на выбранную дату"
    slot_id = slots[0].get("id")



    user_token = get_token("user")
    booking_data = {
        "slotId": slot_id,
        "conferenceLink": False
    }
    create_booking_resp = requests.post(
        f"{BASE_URL}/bookings/create",
        json=booking_data,
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert create_booking_resp.status_code == 201
    booking = create_booking_resp.json()
    booking_id = booking.get("id")
    assert booking["status"] == "active"



    my_bookings_resp = requests.get(
        f"{BASE_URL}/bookings/my",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert my_bookings_resp.status_code == 200
    my_bookings = my_bookings_resp.json()
    assert any(b.get("id") == booking_id for b in my_bookings)


    cancel_resp = requests.post(
        f"{BASE_URL}/bookings/{booking_id}/cancel",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert cancel_resp.status_code == 200

    cancel_resp2 = requests.post(
        f"{BASE_URL}/bookings/{booking_id}/cancel",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert cancel_resp2.status_code == 200
    

if __name__ == "__main__":
    test_full_booking_flow()
