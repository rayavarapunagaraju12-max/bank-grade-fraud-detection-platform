# Architecture Overview

```mermaid
flowchart LR
  API[FastAPI Transaction API] --> Kafka[(Kafka)]
  Kafka --> Features[Streaming Feature Engineering]
  Features --> Redis[(Redis)]
  Features --> Graph[Neo4j Graph Builder]
  Graph --> GraphFeatures[Graph Features]
  Redis --> Ensemble[Tabular + Anomaly + Graph Ensemble]
  GraphFeatures --> Ensemble
  Ensemble --> Cases[(PostgreSQL Cases)]
  Ensemble --> Explain[SHAP + Ollama Narrative]
  Cases --> Frontend[React Case Management]
```

Transactions are keyed by `account_id`, which lets Kafka partition related account behavior consistently. Redis stores short-lived velocity, merchant, device, IP, and beneficiary counters. Neo4j stores the entity network and supports graph features used by the ensemble scorer.
