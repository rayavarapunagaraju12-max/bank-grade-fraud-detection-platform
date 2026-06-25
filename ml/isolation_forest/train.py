from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest

FEATURES = ["amount", "account_velocity_5m", "device_reuse_24h", "ip_reuse_24h", "graph_degree"]


def train(
    input_csv: str = "data/synthetic/transactions.csv",
    output: str = "training/model_registry/isolation_forest.joblib",
) -> None:
    df = pd.read_csv(input_csv)
    model = IsolationForest(n_estimators=100, contamination=0.03, random_state=42)
    model.fit(df[FEATURES])
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "features": FEATURES}, output)


if __name__ == "__main__":
    train()
