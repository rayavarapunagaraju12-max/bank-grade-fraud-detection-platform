from streaming.transaction_generator.generator import make_transaction


def generate_fraud_ring(size: int = 1000) -> list[dict]:
    return [make_transaction(i, fraud_ring=True) for i in range(size)]


def generate_money_laundering_chain(length: int = 25) -> list[dict]:
    chain = []
    for i in range(length):
        txn = make_transaction(i, fraud_ring=True)
        txn["account_id"] = f"acct_chain_{i}"
        txn["beneficiary_id"] = f"acct_chain_{i + 1}"
        txn["merchant_id"] = "m_wire"
        chain.append(txn)
    return chain


def generate_device_sharing_attack(accounts: int = 50) -> list[dict]:
    events = []
    for i in range(accounts):
        txn = make_transaction(i, fraud_ring=True)
        txn["account_id"] = f"acct_device_attack_{i}"
        txn["device_id"] = "device_shared_attack"
        events.append(txn)
    return events
