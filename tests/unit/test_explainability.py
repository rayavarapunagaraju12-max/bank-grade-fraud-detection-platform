from ml.shap.explainer import IMPORTANT_FEATURES, explain_features


def test_proxy_explanation_returns_all_important_features() -> None:
    explanation = explain_features(
        {
            "amount": 5000,
            "account_velocity_5m": 8,
            "device_reuse_24h": 4,
            "shortest_path_to_fraud": 2,
        },
        score=0.82,
    )

    assert explanation["mode"] in {"proxy", "tree_shap"}
    returned = {item["feature"] for item in explanation["features"]}
    assert set(IMPORTANT_FEATURES).issubset(returned)
    assert explanation["model_score"] == 0.82
