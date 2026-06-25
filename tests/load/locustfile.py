from locust import HttpUser, between, task

from streaming.transaction_generator.generator import make_transaction


class FraudApiUser(HttpUser):
    wait_time = between(0.01, 0.05)

    @task
    def ingest(self) -> None:
        self.client.post("/transactions", json=make_transaction(1))
