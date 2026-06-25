from ml.ensemble.service import EnsembleScorer


def test_ensemble_score_bounds() -> None:
    score = EnsembleScorer().score(
        {
            "amount": 5000,
            "account_velocity_5m": 30,
            "device_reuse_24h": 10,
            "ip_reuse_24h": 10,
        }
    )
    assert 0 <= score["fraud_score"] <= 1
    assert score["fraud_score"] > 0.5
