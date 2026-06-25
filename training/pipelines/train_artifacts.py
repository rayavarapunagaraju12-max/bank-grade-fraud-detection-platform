from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

FEATURES = ["amount", "account_velocity_5m", "device_reuse_24h", "ip_reuse_24h", "graph_degree"]


def train_artifacts(
    input_csv: str = "data/synthetic/transactions.csv",
    output_dir: str = "training/model_registry",
) -> dict:
    df = pd.read_csv(input_csv)
    df = _expand_tiny_dataset(df)
    y = df["is_fraud"].astype(int)
    x = df[FEATURES]
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42, stratify=y)

    tabular = RandomForestClassifier(n_estimators=80, max_depth=8, random_state=42, class_weight="balanced")
    tabular.fit(x_train, y_train)

    anomaly = IsolationForest(n_estimators=100, contamination=max(float(y.mean()), 0.01), random_state=42)
    anomaly.fit(x_train)

    train_meta = pd.DataFrame(
        {
            "tabular_score": tabular.predict_proba(x_train)[:, 1],
            "anomaly_score": _anomaly_scores(anomaly, x_train),
            "graph_score": _graph_scores(x_train),
        }
    )
    meta = LogisticRegression(random_state=42, class_weight="balanced")
    meta.fit(train_meta, y_train)

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    tabular_artifact = {"model": tabular, "features": FEATURES, "score": tabular.score(x_test, y_test)}
    joblib.dump(tabular_artifact, output / "xgboost.joblib")
    joblib.dump({"model": anomaly, "features": FEATURES}, output / "isolation_forest.joblib")
    joblib.dump(
        {"model": meta, "features": ["tabular_score", "anomaly_score", "graph_score"]},
        output / "meta_learner.joblib",
    )
    return {"artifacts": ["xgboost.joblib", "isolation_forest.joblib", "meta_learner.joblib"]}


def _anomaly_scores(model: IsolationForest, frame: pd.DataFrame) -> list[float]:
    return [max(0.0, min(1.0, 0.5 - float(value))) for value in model.decision_function(frame)]


def _graph_scores(frame: pd.DataFrame) -> list[float]:
    return [max(0.0, min(1.0, float(row.graph_degree) / 20)) for row in frame.itertuples()]


def _expand_tiny_dataset(df: pd.DataFrame) -> pd.DataFrame:
    if len(df) >= 30:
        return df
    rows = []
    for idx in range(12):
        for row in df.to_dict("records"):
            updated = dict(row)
            multiplier = 1 + (idx - 6) * 0.015
            updated["amount"] = max(1.0, float(updated["amount"]) * multiplier)
            updated["account_velocity_5m"] = max(0, int(updated["account_velocity_5m"]) + (idx % 3) - 1)
            updated["device_reuse_24h"] = max(0, int(updated["device_reuse_24h"]) + (idx % 2))
            updated["ip_reuse_24h"] = max(0, int(updated["ip_reuse_24h"]) + (idx % 2))
            updated["graph_degree"] = max(0, int(updated["graph_degree"]) + (idx % 4) - 1)
            rows.append(updated)
    return pd.DataFrame(rows)


if __name__ == "__main__":
    print(train_artifacts())
