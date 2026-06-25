SANCTIONED_COUNTRIES = {"IR", "KP", "SY"}
HIGH_RISK_MERCHANTS = {"m_crypto", "m_wire"}


def evaluate_rules(transaction: dict, features: dict) -> list[dict]:
    hits = []
    if transaction.get("country") in SANCTIONED_COUNTRIES:
        hits.append({"rule": "sanctioned_country", "severity": "critical"})
    if float(transaction.get("amount", 0)) > 10000:
        hits.append({"rule": "large_transaction", "severity": "high"})
    if int(features.get("account_velocity_5m", 0)) > 20:
        hits.append({"rule": "velocity_limit_5m", "severity": "high"})
    if transaction.get("merchant_id") in HIGH_RISK_MERCHANTS and float(transaction.get("amount", 0)) > 1000:
        hits.append({"rule": "high_risk_merchant_amount", "severity": "medium"})
    return hits
