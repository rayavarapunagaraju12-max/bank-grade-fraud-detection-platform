import pytest

from ml.ensemble.service import EnsembleScorer


@pytest.mark.regression
def test_high_risk_fixture_stays_high_risk() -> None:
    score = EnsembleScorer().score(
        {
            "amount": 9200,
            "account_velocity_5m": 31,
            "device_reuse_24h": 18,
            "ip_reuse_24h": 14,
            "graph_degree": 22,
            "shortest_path_to_fraud": 2,
        }
    )
    assert score["fraud_score"] >= 0.75
