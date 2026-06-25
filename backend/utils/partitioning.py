import hashlib


def account_partition(account_id: str, partitions: int = 12) -> int:
    digest = hashlib.sha256(account_id.encode("utf-8")).hexdigest()
    return int(digest, 16) % partitions
