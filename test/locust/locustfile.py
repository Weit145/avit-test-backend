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
            "/rooms/1500c460-133b-4e70-a7ac-5d20b5275a2e/slots/list",
            params={"date": "2026-04-26"},
            headers={"Authorization": f"Bearer {self.token}"},
        )
