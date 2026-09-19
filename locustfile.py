from locust import HttpUser, task, between

class GestMatUser(HttpUser):
    wait_time = between(1, 5)
    token = None

    def on_start(self):
        """On start, login and get the JWT token"""
        response = self.client.post("/api/auth/login/", json={
            "username": "locust_test",
            "password": "LocustPass123!"
        })
        if response.status_code == 200:
            self.token = response.json().get("access")

    @task(2)
    def get_estudiantes(self):
        if self.token:
            self.client.get("/api/estudiante/", headers={"Authorization": f"Bearer {self.token}"})

    @task(2)
    def get_matriculas(self):
        if self.token:
            self.client.get("/api/matricula/", headers={"Authorization": f"Bearer {self.token}"})

