from compliance.rule_engine.rules import evaluate_rules


def test_velocity_rule_triggers() -> None:
    hits = evaluate_rules({"amount": 50, "country": "US", "merchant_id": "m_grocery"}, {"account_velocity_5m": 25})
    assert any(hit["rule"] == "velocity_limit_5m" for hit in hits)
