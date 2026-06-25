from pathlib import Path
from typing import Any

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap

MODEL_PATH = Path("training/model_registry/xgboost.joblib")
IMPORTANT_FEATURES = [
    "amount",
    "account_velocity_5m",
    "account_velocity_1h",
    "device_reuse_24h",
    "ip_reuse_24h",
    "merchant_frequency_24h",
    "graph_degree",
    "shortest_path_to_fraud",
]

_TREE_EXPLAINER: Any | None = None
_TREE_FEATURES: list[str] | None = None


def explain_features(features: dict, score: float) -> dict:
    tree_explanation = _try_tree_shap(features, score)
    if tree_explanation is not None:
        return tree_explanation
    return _proxy_explanation(features, score)


def _try_tree_shap(features: dict, score: float) -> dict | None:
    explainer, feature_names = _load_tree_explainer()
    if explainer is None or feature_names is None:
        return None

    frame = pd.DataFrame([{name: _number(features, name) for name in feature_names}])
    shap_values = explainer.shap_values(frame)
    values = _first_explanation_vector(shap_values)
    base_value = explainer.expected_value
    if isinstance(base_value, list):
        base_value = base_value[-1]
    if isinstance(base_value, np.ndarray):
        base_value = base_value.reshape(-1)[-1]

    contributions = [
        {
            "feature": name,
            "value": float(frame.iloc[0][name]),
            "contribution": round(float(value), 4),
        }
        for name, value in zip(feature_names, values, strict=False)
    ]
    returned = {item["feature"] for item in contributions}
    for name in IMPORTANT_FEATURES:
        if name not in returned:
            contributions.append({"feature": name, "value": _number(features, name), "contribution": 0.0})

    return {
        "mode": "tree_shap",
        "base_value": float(base_value),
        "model_score": score,
        "features": sorted(contributions, key=lambda item: abs(item["contribution"]), reverse=True),
    }


def _load_tree_explainer() -> tuple[Any | None, list[str] | None]:
    global _TREE_EXPLAINER, _TREE_FEATURES

    if _TREE_EXPLAINER is not None:
        return _TREE_EXPLAINER, _TREE_FEATURES
    if not MODEL_PATH.exists():
        return None, None

    artifact = joblib.load(MODEL_PATH)
    if not isinstance(artifact, dict) or "model" not in artifact:
        return None, None

    _TREE_FEATURES = list(artifact.get("features") or IMPORTANT_FEATURES)
    _TREE_EXPLAINER = shap.TreeExplainer(artifact["model"])
    return _TREE_EXPLAINER, _TREE_FEATURES


def _first_explanation_vector(shap_values: Any) -> np.ndarray:
    if isinstance(shap_values, list):
        values = np.asarray(shap_values[-1])
    else:
        values = np.asarray(shap_values)
    if values.ndim == 3:
        return values[0, :, -1]
    if values.ndim == 2:
        return values[0]
    return values.reshape(-1)


def _proxy_explanation(features: dict, score: float) -> dict:
    contributions = []
    for name in IMPORTANT_FEATURES:
        value = _number(features, name)

        if name == "amount":
            contribution = min(0.25, abs(value) / 1000)
        elif name == "shortest_path_to_fraud":
            contribution = 0.2 if value <= 2 else 0.02
        else:
            contribution = min(0.2, value / 20)

        contributions.append(
            {"feature": name, "value": value, "contribution": round(contribution, 4)}
        )

    return {
        "mode": "proxy",
        "base_value": 0.05,
        "model_score": score,
        "features": sorted(contributions, key=lambda item: abs(item["contribution"]), reverse=True),
    }


def save_waterfall_plot(explanation: dict, output: str) -> str:
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    labels = [item["feature"] for item in explanation["features"][:8]]
    values = [item["contribution"] for item in explanation["features"][:8]]
    plt.figure(figsize=(10, 5))
    plt.barh(labels, values)
    plt.xlabel(f"{explanation.get('mode', 'shap')} contribution")
    plt.tight_layout()
    plt.savefig(output)
    plt.close()
    return output


def _number(features: dict, name: str, default: float = 0.0) -> float:
    value = features.get(name, default)
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
