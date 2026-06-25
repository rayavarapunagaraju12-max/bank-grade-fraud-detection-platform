import argparse
import random
import time
import uuid
from datetime import UTC, datetime

from backend.services.kafka import KafkaPublisher

MERCHANTS = ["m_airline", "m_crypto", "m_grocery", "m_electronics", "m_wire"]
CHANNELS = ["card_present", "card_not_present", "wire", "ach", "atm"]
RNG = random.SystemRandom()


def make_transaction(i: int, fraud_ring: bool = False) -> dict:
    account_pool = 200 if fraud_ring else 10000
    shared_device = (
        "device_ring_001"
        if fraud_ring and RNG.random() < 0.65
        else f"device_{RNG.randint(1, 20000)}"
    )
    shared_ip = (
        "185.199.10.12"
        if fraud_ring and RNG.random() < 0.5
        else f"10.{RNG.randint(1, 255)}.{RNG.randint(1, 255)}.{RNG.randint(1, 255)}"
    )
    return {
        "transaction_id": f"txn_{int(time.time() * 1000)}_{i}_{uuid.uuid4().hex[:6]}",
        "account_id": f"acct_{RNG.randint(1, account_pool)}",
        "amount": round(RNG.lognormvariate(3.2 if not fraud_ring else 4.6, 1.0), 2),
        "currency": "USD",
        "merchant_id": RNG.choice(MERCHANTS),
        "merchant_category": RNG.choice(["grocery", "travel", "crypto", "electronics", "money_transfer"]),
        "device_id": shared_device,
        "ip_address": shared_ip,
        "beneficiary_id": f"bene_{RNG.randint(1, 500 if fraud_ring else 5000)}",
        "channel": RNG.choice(CHANNELS),
        "country": RNG.choice(["US", "US", "US", "CA", "GB", "NG", "RU"]),
        "timestamp": datetime.now(UTC).isoformat(),
    }


def run(rate: int, seconds: int, fraud_ratio: float) -> None:
    publisher = KafkaPublisher()
    interval = 1 / max(rate, 1)
    deadline = None if seconds <= 0 else time.time() + seconds
    i = 0
    try:
        while deadline is None or time.time() < deadline:
            publisher.publish_transaction(make_transaction(i, RNG.random() < fraud_ratio))
            i += 1
            if i % max(rate, 1) == 0:
                publisher.flush()
            if rate < 10000:
                time.sleep(interval)
    finally:
        publisher.flush()
        print(f"generated={i}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rate", type=int, default=1000)
    parser.add_argument("--seconds", type=int, default=30, help="Use 0 or less to run continuously")
    parser.add_argument("--fraud-ratio", type=float, default=0.03)
    args = parser.parse_args()
    run(args.rate, args.seconds, args.fraud_ratio)
