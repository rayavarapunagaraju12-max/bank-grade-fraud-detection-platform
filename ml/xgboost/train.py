from pathlib import Path

import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

FEATURES = ["amount", "account_velocity_5m", "device_reuse_24h", "ip_reuse_24h", "graph_degree"]


def train(
    input_csv: str = "data/synthetic/transactions.csv",
    output: str = "training/model_registry/xgboost.joblib",
) -> None:
    df = pd.read_csv(input_csv)
    y = df["is_fraud"]
    X = df[FEATURES]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    model = XGBClassifier(n_estimators=150, max_depth=5, learning_rate=0.05, eval_metric="auc")
    model.fit(X_train, y_train)
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "features": FEATURES, "score": model.score(X_test, y_test)}, output)


if __name__ == "__main__":
    train()
