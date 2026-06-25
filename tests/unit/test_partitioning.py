from backend.utils.partitioning import account_partition


def test_account_partition_is_stable() -> None:
    assert account_partition("acct_123", 12) == account_partition("acct_123", 12)
    assert 0 <= account_partition("acct_123", 12) < 12
