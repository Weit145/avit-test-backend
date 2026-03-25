from locust import HttpUser, task, between


class SlotUser(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        resp = self.client.post("/dummyLogin/", json="user")

        if resp.status_code != 200:
            raise Exception(f"Login failed: {resp.status_code}, {resp.text}")

        try:
            data = resp.json()
        except Exception:
            raise Exception(f"Invalid JSON response: {resp.text}")

        self.token = data["jwt"]

    @task
    def get_slots(self):
        self.client.get(
            "/rooms/8e07d1bc-f10d-4e9f-81c4-4381a4f9b623/slots/list",
            params={"date": "2026-04-26"},
            headers={"Authorization": f"Bearer {self.token}"},
        )
