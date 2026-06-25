import csv
from pathlib import Path

from streaming.transaction_generator.generator import make_transaction


def generate(path: str = "data/synthetic/transactions.csv", rows: int = 5000) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "amount",
                "account_velocity_5m",
                "device_reuse_24h",
                "ip_reuse_24h",
                "graph_degree",
                "is_fraud",
            ],
        )
        writer.writeheader()
        for i in range(rows):
            fraud = i % 25 == 0
            txn = make_transaction(i, fraud)
            writer.writerow(
                {
                    "amount": txn["amount"],
                    "account_velocity_5m": 30 if fraud else 2,
                    "device_reuse_24h": 15 if fraud else 1,
                    "ip_reuse_24h": 12 if fraud else 1,
                    "graph_degree": 18 if fraud else 3,
                    "is_fraud": int(fraud),
                }
            )


if __name__ == "__main__":
    generate()
