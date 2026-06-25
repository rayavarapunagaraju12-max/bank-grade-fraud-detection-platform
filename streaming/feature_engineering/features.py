import json
import time
from collections import defaultdict
from datetime import UTC, datetime
from typing import cast

import redis

from backend.config import get_settings


class StreamingFeatureEngineer:
    def __init__(self) -> None:
        self.redis = redis.Redis.from_url(get_settings().redis_url, decode_responses=True)
        self.memory = InMemoryFeatureEngineer()
        self.use_redis = True
        try:
            self.redis.ping()
        except Exception:
            self.use_redis = False

    def compute(self, txn: dict) -> dict:
        if not self.use_redis:
            return self.memory.compute(txn)
        now = datetime.fromisoformat(str(txn["timestamp"]).replace("Z", "+00:00"))
        if now.tzinfo is None:
            now = now.replace(tzinfo=UTC)
        ts = int(now.timestamp())
        account = txn["account_id"]
        amount = float(txn["amount"])
        pipe = self.redis.pipeline()
        windows = {"5m": 300, "1h": 3600, "24h": 86400}
        for suffix, ttl in windows.items():
            key = f"acct:{account}:txns:{suffix}"
            pipe.zadd(key, {json.dumps({"t": txn["transaction_id"], "a": amount}): ts})
            pipe.zremrangebyscore(key, 0, ts - ttl)
            pipe.expire(key, ttl + 60)
        for dimension in ("merchant_id", "device_id", "ip_address", "beneficiary_id"):
            value = txn.get(dimension)
            if value:
                key = f"{dimension}:{value}:accounts:24h"
                pipe.sadd(key, account)
                pipe.expire(key, 86500)
        try:
            pipe.execute()
        except Exception:
            self.use_redis = False
            return self.memory.compute(txn)

        one_hour = cast(list[str], self.redis.zrange(f"acct:{account}:txns:1h", 0, -1))
        amounts = [json.loads(row)["a"] for row in one_hour] if one_hour else []
        avg_amount = sum(amounts) / len(amounts) if amounts else amount
        return {
            "transaction_id": txn["transaction_id"],
            "account_id": account,
            "amount": amount,
            "account_velocity_5m": self.redis.zcard(f"acct:{account}:txns:5m"),
            "account_velocity_1h": self.redis.zcard(f"acct:{account}:txns:1h"),
            "avg_amount_1h": avg_amount,
            "merchant_frequency_24h": self.redis.scard(f"merchant_id:{txn['merchant_id']}:accounts:24h"),
            "device_reuse_24h": self.redis.scard(f"device_id:{txn['device_id']}:accounts:24h"),
            "ip_reuse_24h": self.redis.scard(f"ip_address:{txn['ip_address']}:accounts:24h"),
            "beneficiary_frequency_24h": (
                self.redis.scard(f"beneficiary_id:{txn.get('beneficiary_id')}:accounts:24h")
                if txn.get("beneficiary_id")
                else 0
            ),
        }


class InMemoryFeatureEngineer:
    def __init__(self) -> None:
        self.events: dict[str, list[tuple[int, float]]] = defaultdict(list)
        self.dimension_accounts: dict[str, set[str]] = defaultdict(set)

    def compute(self, txn: dict) -> dict:
        now = int(time.time())
        account = txn["account_id"]
        amount = float(txn["amount"])
        self.events[account].append((now, amount))
        self.events[account] = [(ts, amt) for ts, amt in self.events[account] if ts >= now - 86400]
        for dimension in ("merchant_id", "device_id", "ip_address", "beneficiary_id"):
            value = txn.get(dimension)
            if value:
                self.dimension_accounts[f"{dimension}:{value}"].add(account)
        one_hour = [amt for ts, amt in self.events[account] if ts >= now - 3600]
        return {
            "transaction_id": txn["transaction_id"],
            "account_id": account,
            "amount": amount,
            "account_velocity_5m": len([event for event in self.events[account] if event[0] >= now - 300]),
            "account_velocity_1h": len(one_hour),
            "avg_amount_1h": sum(one_hour) / len(one_hour) if one_hour else amount,
            "merchant_frequency_24h": len(self.dimension_accounts[f"merchant_id:{txn['merchant_id']}"]),
            "device_reuse_24h": len(self.dimension_accounts[f"device_id:{txn['device_id']}"]),
            "ip_reuse_24h": len(self.dimension_accounts[f"ip_address:{txn['ip_address']}"]),
            "beneficiary_frequency_24h": (
                len(self.dimension_accounts[f"beneficiary_id:{txn.get('beneficiary_id')}"])
                if txn.get("beneficiary_id")
                else 0
            ),
        }
