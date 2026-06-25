import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

DEFAULT_MODEL_DIR = Path("training/model_registry")
DEFAULT_TABULAR_FEATURES = [
    "amount",
    "account_velocity_5m",
    "device_reuse_24h",
    "ip_reuse_24h",
    "graph_degree",
]


@dataclass(frozen=True)
class ModelArtifactStatus:
    name: str
    path: Path
    loaded: bool
    reason: str


@dataclass
class LoadedArtifact:
    model: Any
    features: list[str]


class EnsembleScorer:
    """Fraud score orchestrator with production artifact hooks and a local fallback."""

    def __init__(self, model_dir: str | Path = DEFAULT_MODEL_DIR) -> None:
        self.model_dir = Path(model_dir)
        self.tabular_model = self._load_artifact("xgboost", "xgboost.joblib")
        self.anomaly_model = self._load_artifact("isolation_forest", "isolation_forest.joblib")
        self.meta_model = self._load_artifact("meta_learner", "meta_learner.joblib")
        self.artifact_status = [
            self._status("xgboost", "xgboost.joblib", self.tabular_model),
            self._status("isolation_forest", "isolation_forest.joblib", self.anomaly_model),
            self._status("meta_learner", "meta_learner.joblib", self.meta_model),
        ]

    def score(self, features: dict) -> dict:
        tabular_score = self._score_tabular(features)
        anomaly_score = self._score_anomaly(features)
        graph_score = self._score_graph(features)
        fraud_score = self._score_meta(tabular_score, anomaly_score, graph_score)

        return {
            "fraud_score": round(self._bounded(fraud_score), 4),
            "tabular_score": round(self._bounded(tabular_score), 4),
            "anomaly_score": round(self._bounded(anomaly_score), 4),
            "graph_score": round(self._bounded(graph_score), 4),
            "model_mode": self.model_mode,
        }

    @property
    def model_mode(self) -> str:
        loaded = [status.name for status in self.artifact_status if status.loaded]
        return "artifact-backed" if loaded else "deterministic-fallback"

    def _load_artifact(self, name: str, filename: str) -> LoadedArtifact | None:
        path = self.model_dir / filename
        if not path.exists():
            return None

        artifact = joblib.load(path)
        if not isinstance(artifact, dict) or "model" not in artifact:
            raise ValueError(f"{name} artifact must be a dict containing a 'model' key")

        features = artifact.get("features") or DEFAULT_TABULAR_FEATURES
        return LoadedArtifact(model=artifact["model"], features=list(features))

    def _status(self, name: str, filename: str, artifact: LoadedArtifact | None) -> ModelArtifactStatus:
        path = self.model_dir / filename
        if artifact is None:
            return ModelArtifactStatus(name=name, path=path, loaded=False, reason="artifact not found")
        return ModelArtifactStatus(name=name, path=path, loaded=True, reason="loaded")

    def _score_tabular(self, features: dict) -> float:
        if self.tabular_model is not None:
            frame = self._feature_frame(features, self.tabular_model.features)
            if hasattr(self.tabular_model.model, "predict_proba"):
                return float(self.tabular_model.model.predict_proba(frame)[0][1])
            return float(self.tabular_model.model.predict(frame)[0])

        amount = self._number(features, "amount")
        velocity = self._number(features, "account_velocity_5m")
        device_reuse = self._number(features, "device_reuse_24h")
        ip_reuse = self._number(features, "ip_reuse_24h")
        return self._sigmoid((amount - 250) / 700 + velocity / 12 + device_reuse / 8 + ip_reuse / 8)

    def _score_anomaly(self, features: dict) -> float:
        if self.anomaly_model is not None:
            frame = self._feature_frame(features, self.anomaly_model.features)
            if hasattr(self.anomaly_model.model, "decision_function"):
                raw_score = float(self.anomaly_model.model.decision_function(frame)[0])
                return self._bounded(0.5 - raw_score)
            if hasattr(self.anomaly_model.model, "predict"):
                return 1.0 if int(self.anomaly_model.model.predict(frame)[0]) == -1 else 0.0

        amount = self._number(features, "amount")
        avg_amount = self._number(features, "avg_amount_1h", default=amount)
        velocity = self._number(features, "account_velocity_5m")
        deviation = abs(amount - avg_amount) / max(amount, 1)
        return self._bounded(deviation + velocity / 50)

    def _score_graph(self, features: dict) -> float:
        graph_degree = self._number(features, "graph_degree")
        path_to_fraud = self._number(features, "shortest_path_to_fraud", default=99)
        device_reuse = self._number(features, "device_reuse_24h")
        ip_reuse = self._number(features, "ip_reuse_24h")
        shared_device_count = self._number(features, "shared_device_count")
        shared_ip_count = self._number(features, "shared_ip_count")
        fraud_ring_score = self._number(features, "fraud_ring_score")

        return self._bounded(
            graph_degree / 20
            + 1 / max(path_to_fraud, 1)
            + device_reuse / 20
            + ip_reuse / 20
            + shared_device_count / 25
            + shared_ip_count / 25
            + fraud_ring_score * 0.35
        )

    def _score_meta(self, tabular: float, anomaly: float, graph: float) -> float:
        if self.meta_model is not None:
            frame = pd.DataFrame(
                [{"tabular_score": tabular, "anomaly_score": anomaly, "graph_score": graph}]
            )
            if hasattr(self.meta_model.model, "predict_proba"):
                return float(self.meta_model.model.predict_proba(frame)[0][1])
            return float(self.meta_model.model.predict(frame)[0])

        return 0.45 * tabular + 0.25 * anomaly + 0.30 * graph

    @staticmethod
    def _feature_frame(features: dict, names: list[str]) -> pd.DataFrame:
        return pd.DataFrame([{name: EnsembleScorer._number(features, name) for name in names}])

    @staticmethod
    def _number(features: dict, name: str, default: float = 0.0) -> float:
        value = features.get(name, default)
        if value is None:
            return default
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _bounded(value: float) -> float:
        return max(0.0, min(1.0, value))

    @staticmethod
    def _sigmoid(value: float) -> float:
        return 1 / (1 + math.exp(-value))
