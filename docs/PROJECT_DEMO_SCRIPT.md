# Bank-Grade Real-Time Fraud Detection Platform Demo Script

This script is based on the current repository state. It describes implemented or scaffolded features found in the codebase and documentation. Do not present this as a fully deployed bank production system. Present it as a production-style portfolio and pilot-ready demo that still needs cloud hardening, managed secrets, SSO/OIDC, official-feed operations, production Kubernetes validation, and formal security/compliance review.

## 1. Demo Timeline

| Time | Section | Screen | What to Show |
|---|---|---|---|
| 0:00-0:20 | Introduction | GitHub Repository or README | Project name, purpose, and stack summary. |
| 0:20-0:40 | Problem Statement | README / Dashboard | Fraud teams need fast scoring, explanations, investigation workflow, and audit evidence. |
| 0:40-1:10 | Architecture | `docs/diagrams/architecture.mmd` or rendered diagram | React, FastAPI, Kafka, Redis, PostgreSQL, Neo4j, ML, SHAP, compliance, monitoring. |
| 1:10-1:35 | Live Dashboard | FraudOps Dashboard | Open metrics, recent transactions, risk summary, API status. |
| 1:35-1:55 | Generate Fraud Case | FraudOps Dashboard -> Alert Queue | Click `Generate AI Fraud Case`; show alert appears. |
| 1:55-2:20 | Investigation | Investigation Workspace + Graph Visualization | Show score, reasons, narrative, workflow actions, and graph context. |
| 2:20-2:40 | Compliance & Governance | Compliance Reports / DLQ / Model Governance | Show watchlists, sanctions screening, India STR draft, audit/DLQ/model lifecycle screens. |
| 2:40-2:50 | Monitoring & Infrastructure | Swagger UI / Prometheus / Grafana / Kibana / MinIO | Briefly show operational surfaces and explain optional full-stack services. |
| 2:50-3:00 | Conclusion | Pilot Readiness | Summarize what works today and what remains for production. |

## 2. Screen Recording Guide

1. **0:00 - GitHub Repository or README**
   - Open `README.md`.
   - Say the project is a production-style fraud detection platform for portfolio, demo, and pilot review.
   - Do not claim live bank production readiness.

2. **0:20 - FraudOps Dashboard**
   - Open `http://localhost:5173`.
   - Login with a seeded demo user if prompted.
   - Show API status, totals, fraud rate, and live transaction list.

3. **0:40 - Architecture Diagram**
   - Open `docs/diagrams/architecture.mmd` or a rendered Mermaid preview.
   - Point to the path from UI/API to Kafka, Redis, Neo4j, PostgreSQL, ML scoring, explanations, alerts, compliance, and monitoring.

4. **1:10 - FraudOps Dashboard**
   - Return to the dashboard.
   - Click `Generate AI Fraud Case`.
   - Explain that `/demo/generate?fraud_ring=true` creates a risky transaction using shared device/IP behavior.

5. **1:35 - Fraud Alert Queue**
   - Switch to `Fraud Alert Queue`.
   - Show risk-ranked alerts, transaction ID, risk band, score, and status.

6. **1:55 - Investigation Workspace**
   - Switch to `Investigation Workspace`.
   - Show transaction details, score, model explanation, AI fraud narrative, and workflow buttons.
   - Demonstrate one workflow action only if safe, for example `Investigate`.

7. **2:10 - Graph Visualization**
   - Switch to `Graph Visualization`.
   - Show account, device, IP, merchant, and relationship context.

8. **2:20 - Compliance Reports**
   - Switch to `Compliance Reports`.
   - Show demo watchlist refresh, sanctions screening, and India STR-style draft generation.

9. **2:30 - Model Governance / DLQ Monitoring**
   - Open `Model Governance` and `DLQ Monitoring`.
   - Explain model lifecycle records and dead-letter message handling.

10. **2:40 - Swagger UI**
    - Open `http://localhost:8000/docs`.
    - Show endpoints: `/transactions`, `/alerts`, `/dashboard/summary`, `/models/status`, `/compliance/*`, `/dlq/messages`, `/graph/{account_id}`, `/metrics`.

11. **2:45 - Optional Infra Screens**
    - Prometheus: `http://localhost:9090`
    - Grafana: `http://localhost:3000`
    - Kibana: `http://localhost:5601`
    - Neo4j: `http://localhost:7474`
    - MinIO: `http://localhost:9001`
    - Explain these are available in full compose profiles, while the laptop demo can run a lighter stack.

12. **2:50 - Pilot Readiness**
    - End on `Pilot Readiness`.
    - State demo/pilot strengths and production hardening gaps.

## 3. Voice-Over Script

### 0:00-0:20 Introduction

"This is my Bank-Grade Real-Time Fraud Detection Platform. It is a production-style project that demonstrates how a bank or fintech could detect risky transactions, explain why they were flagged, and support analyst investigation. The stack includes React, FastAPI, Kafka, Redis, PostgreSQL, Neo4j, machine learning, explainability, compliance workflows, and monitoring."

### 0:20-0:40 Problem Statement

"The problem is that fraud teams need more than a model score. They need fast transaction screening, clear reasons for each alert, relationship context across accounts and devices, and an audit trail for compliance. This project connects those pieces into one workflow."

### 0:40-1:10 Architecture

"The frontend is a React FraudOps console. It talks to a FastAPI backend. Transactions can enter through the API or Kafka. Redis stores short-term velocity features, Neo4j stores account and entity relationships, and PostgreSQL stores transactions, alerts, audit logs, compliance reports, users, DLQ records, and model governance data. The scoring layer combines tabular, anomaly, and graph signals, then returns SHAP-style explanations and an investigation narrative."

### 1:10-1:35 Dashboard

"This dashboard is the analyst starting point. It shows recent transactions, fraud rate, average risk score, open alerts, and API status. The data comes from the backend summary and alert endpoints, and the page refreshes automatically."

### 1:35-1:55 Generate Case and Alert Queue

"I will generate a demo fraud case. The demo endpoint creates a transaction with suspicious behavior, including high-risk merchant activity and shared device or IP patterns. The system scores it, applies rules, stores the transaction, and creates an alert when the risk is high enough."

### 1:55-2:20 Investigation and Graph

"In the investigation workspace, the analyst sees transaction details, risk score, top contributing features, and a narrative explaining the alert. The workflow lets the analyst investigate, escalate, confirm fraud, mark a false positive, or record SAR filing. The graph view adds relationship context, such as accounts sharing a device, IP address, merchant, or beneficiary."

### 2:20-2:40 Compliance and Governance

"The compliance workspace includes demo watchlist ingestion, sanctions screening, and India STR-style report generation. The backend also writes hash-linked audit records for important actions. Model governance tracks model versions and lifecycle transitions, and the DLQ screen supports controlled replay of failed stream messages."

### 2:40-2:50 Monitoring and Infrastructure

"The platform exposes FastAPI Swagger documentation and Prometheus metrics. The full Docker stack includes Kafka, Redis, PostgreSQL, Neo4j, MinIO, Prometheus, Grafana, Elasticsearch, Logstash, Kibana, and Ollama. Kubernetes manifests and a Helm chart are included as deployment scaffolding."

### 2:50-3:00 Conclusion

"The main value is the end-to-end workflow: ingest a transaction, score it, explain it, investigate it, and preserve compliance evidence. The demo is ready for portfolio and pilot discussion. A real bank rollout would still require managed secrets, SSO, official feed operations, cloud load testing, and formal security review."

## 4. Feature Explanations

### React

- **What it does:** Implements the FraudOps console in `frontend/src`, including dashboard, alert queue, investigation, graph, live stream, compliance, model governance, DLQ, monitoring, and readiness pages.
- **Why it is used:** React supports interactive analyst workflows with reusable TypeScript components.
- **Business value:** Analysts can see alerts, review evidence, and update case status from one UI.
- **Current status:** Implemented frontend that calls real backend endpoints.

### FastAPI

- **What it does:** Provides API routes for health, auth, transaction ingestion, dashboard summaries, alerts, graph lookup, compliance, DLQ, model governance, readiness, and metrics.
- **Why it is used:** FastAPI is fast, typed, and generates Swagger UI automatically.
- **Business value:** Clean API contracts make integration and review easier.
- **Current status:** Implemented in `backend/api/main.py`.

### Kafka

- **What it does:** Provides event streaming for transaction messages, feature events, alerts, and dead-letter publishing.
- **Why banks use it:** Kafka decouples producers and consumers and supports high-throughput event pipelines.
- **How this project uses it:** API and generator can publish transactions; a stream consumer validates messages, computes features, scores, persists alerts, and handles invalid messages through DLQ.
- **Business value:** Enables real-time processing and scalable ingestion.
- **Current status:** Implemented, but the lighter demo compose disables Kafka by default. Full compose includes Kafka and Zookeeper.

### Redis

- **What it does:** Stores short-lived feature windows and graph feature cache.
- **Why banks use it:** Redis is useful for low-latency counters, velocity checks, and cache lookups.
- **How this project uses it:** Streaming feature engineering computes velocity, merchant, device, IP, and beneficiary counters; graph features are cached with TTL.
- **Business value:** Helps detect rapid repeated activity without slow database queries.
- **Current status:** Implemented with in-memory fallback when Redis is unavailable.

### PostgreSQL

- **What it does:** Stores transactions, alerts, audit logs, users, dead letters, watchlists, compliance reports, and model versions.
- **Why it is used:** PostgreSQL is reliable for relational records, investigation history, and audit data.
- **Business value:** Preserves the evidence needed for operations and compliance.
- **Current status:** Implemented with SQLAlchemy models and Alembic migrations.

### Neo4j

- **What it does:** Stores entity relationships between accounts, devices, IPs, merchants, and beneficiaries.
- **Why banks use it:** Fraud rings often appear through shared devices, IPs, beneficiaries, and account networks.
- **How this project uses it:** GraphBuilder upserts relationships; GraphFeatureService computes graph degree, shared device/IP counts, linked accounts, distance to known fraud, and fraud ring score.
- **Business value:** Finds relationship risk that a single transaction model can miss.
- **Current status:** Implemented with in-memory fallback when Neo4j is unavailable.

### Machine Learning

- **What it does:** Scores fraud risk using an ensemble of tabular model, anomaly model, and graph score.
- **Why it is used:** Fraud behavior is multi-signal; combining models can capture different risk patterns.
- **How this project uses it:** `EnsembleScorer` loads XGBoost, Isolation Forest, and meta-learner artifacts from `training/model_registry`; if missing, it uses deterministic fallback scoring.
- **Business value:** Produces a risk score and band for alert prioritization.
- **Current status:** Artifact-backed model path exists and local artifacts are present; fallback is implemented for demo resilience.

### Graph Analytics

- **What it does:** Turns relationships into fraud features such as shared device count, shared IP count, linked account count, graph degree, and path to known fraud.
- **Why it is used:** Fraud rings often reuse infrastructure.
- **Business value:** Improves detection of coordinated activity.
- **Current status:** Implemented in `graph/graph_features/features.py`.

### SHAP Explainability

- **What it does:** Explains which features contributed most to the score.
- **Why it is used:** Analysts and reviewers need understandable reasons.
- **How this project uses it:** Uses SHAP TreeExplainer when the XGBoost artifact is available; otherwise returns proxy feature contributions.
- **Business value:** Makes alerts easier to investigate and defend.
- **Current status:** Implemented with tree SHAP plus fallback.

### LLM Investigation Narratives

- **What it does:** Generates concise analyst narratives based on model explanation and graph findings.
- **Why it is used:** Converts technical signals into readable investigation notes.
- **How this project uses it:** `NarrativeGenerator` calls local Ollama when enabled and falls back to a local template if unavailable.
- **Business value:** Saves analyst time and standardizes evidence summaries.
- **Current status:** Implemented with local fallback; inline LLM generation is disabled in the light demo compose for speed.

### Compliance Module

- **What it does:** Provides sanctions screening, watchlist ingestion, SAR XML export, India STR-style report generation and validation, and audit verification.
- **Why it is used:** Fraud operations must support regulatory review and evidence capture.
- **Business value:** Connects detection to compliance workflow instead of leaving compliance as a manual afterthought.
- **Current status:** Implemented demo/offline services plus official-feed refresh path; production feed operations still need hardening.

### Audit Logs

- **What it does:** Writes hash-linked audit records using SHA-256 and verifies the chain.
- **Why it is used:** Audit logs help prove what happened and detect tampering.
- **Business value:** Supports compliance review and operational accountability.
- **Current status:** Implemented in `compliance/audit_logs/audit.py`.

### Dead Letter Queue

- **What it does:** Captures invalid or failed stream messages and supports controlled replay.
- **Why it is used:** Streaming systems need a safe way to handle bad messages without losing them.
- **Business value:** Improves operational reliability and post-incident analysis.
- **Current status:** Implemented persistence, Kafka DLQ publishing, API listing, and retry endpoint.

### Prometheus

- **What it does:** Scrapes metrics from the API.
- **Why it is used:** Prometheus is a common metric collection system.
- **How this project uses it:** API exposes `/metrics`; `monitoring/prometheus/prometheus.yml` configures scraping.
- **Business value:** Supports operational monitoring.
- **Current status:** Implemented in compose profile.

### Grafana

- **What it does:** Visualizes metrics from Prometheus.
- **Why it is used:** Grafana provides dashboards for service health and trends.
- **Business value:** Helps operators monitor throughput, errors, and system health.
- **Current status:** Compose service and datasource provisioning are present.

### Kibana

- **What it does:** Provides log search and visualization over Elasticsearch.
- **Why it is used:** Centralized logs are important for debugging and investigations.
- **Business value:** Helps teams search service logs during incidents.
- **Current status:** ELK services and Logstash config are present in compose.

### Docker

- **What it does:** Runs the platform services locally with Docker Compose.
- **Why it is used:** Docker makes the demo reproducible across machines.
- **Business value:** Simplifies demo setup and local integration testing.
- **Current status:** Full and light demo compose files exist.

### Kubernetes

- **What it does:** Provides manifests for namespace, API, frontend, stream consumer, transaction generator, and watchlist refresh CronJob.
- **Why it is used:** Kubernetes supports production-style deployment and scaling.
- **Business value:** Shows a path from laptop demo to cloud deployment.
- **Current status:** Scaffolded manifests and Helm chart exist; production cluster validation remains pending.

### MinIO

- **What it does:** Object storage for model artifacts and deployment assets.
- **Why it is used:** MinIO gives S3-compatible storage locally.
- **Business value:** Demonstrates model artifact registry patterns.
- **Current status:** Compose service exists; model artifacts are also present locally in `training/model_registry`.

### GitHub Actions

- **What it does:** Runs backend linting, typing, security scan, model artifact training, unit/model regression tests, and frontend build.
- **Why it is used:** CI catches quality and regression issues before merge.
- **Business value:** Gives reviewers confidence that core checks are automated.
- **Current status:** Implemented in `.github/workflows/ci.yml`; blue-green step is currently an echo placeholder.

## 5. End-to-End Transaction Flow

1. A user or generator submits a transaction through `POST /transactions`, `POST /demo/generate`, `POST /demo/stream/generate`, or Kafka.
2. FastAPI validates the payload with Pydantic transaction schemas.
3. The API stores the transaction in PostgreSQL.
4. If Kafka is enabled, the transaction is published to the Kafka transaction topic using `KafkaPublisher`.
5. Streaming feature engineering computes recent behavior features, including account velocity and reuse counters. Redis is used when available; memory fallback exists.
6. GraphBuilder writes account-device-IP-merchant-beneficiary relationships to Neo4j. If Neo4j is unavailable, an in-memory fallback is used.
7. GraphFeatureService computes graph signals such as graph degree, shared device count, shared IP count, linked accounts, shortest path to known fraud, and fraud ring score. Redis can cache these features.
8. The scoring service builds a feature vector and calls the ensemble scorer.
9. The ensemble combines tabular, anomaly, and graph scores. If local model artifacts are loaded, it uses them; otherwise deterministic fallback scoring is used.
10. SHAP explainability runs using TreeExplainer when the XGBoost artifact is available, otherwise a proxy explanation is returned.
11. Rule checks run for sanctioned countries, large transactions, velocity, and high-risk merchant amounts.
12. The service returns a fraud score and risk band.
13. If the score is at least `0.65` or rules fire, an alert is persisted in PostgreSQL.
14. Audit logging records fraud decisions and workflow changes as hash-linked evidence.
15. The React frontend polls the alert and dashboard endpoints.
16. The alert appears in the FraudOps Dashboard and Fraud Alert Queue.
17. The analyst opens the Investigation Workspace to view details, explanation, narrative, and workflow actions.
18. The analyst can open Graph Visualization, Compliance Reports, Model Governance, DLQ Monitoring, and Monitoring pages for supporting evidence.

## 6. Interview Preparation: 40 Questions

| # | Question | Answer | Follow-up |
|---:|---|---|---|
| 1 | What is this project? | A production-style real-time fraud detection platform with API ingestion, streaming, ML scoring, graph features, explanations, alerts, compliance, audit logs, and monitoring. | What parts are production-ready versus demo-ready? |
| 2 | Why did you build it? | To demonstrate an end-to-end fraud workflow, not only a model notebook. | What business problem does it solve? |
| 3 | What is the main architecture? | React frontend, FastAPI backend, Kafka stream, Redis features, PostgreSQL persistence, Neo4j graph, ML ensemble, SHAP, compliance, and monitoring. | How does a transaction move through it? |
| 4 | Why FastAPI? | It gives typed APIs, Pydantic validation, async support, and Swagger documentation. | How do you secure the API? |
| 5 | What does the React UI include? | Dashboard, alert queue, investigation, graph, live stream, compliance, model governance, DLQ, monitoring, and readiness pages. | Which screen is most important for analysts? |
| 6 | Why Kafka? | Kafka decouples ingestion from processing and supports event-driven transaction pipelines. | How does the consumer handle invalid messages? |
| 7 | How is Redis used? | It stores velocity and reuse features and caches graph features. | What happens if Redis is unavailable? |
| 8 | Why PostgreSQL? | It stores operational records such as transactions, alerts, audits, users, DLQ, watchlists, reports, and model versions. | Which tables are critical? |
| 9 | Why Neo4j? | Neo4j models relationships between accounts, devices, IPs, merchants, and beneficiaries. | What graph features are computed? |
| 10 | What ML models are used? | XGBoost, Isolation Forest, and a meta-learner are loaded from joblib artifacts when present. | What is the fallback mode? |
| 11 | What is the ensemble score? | It combines tabular score, anomaly score, and graph score into one fraud score. | Why combine different signals? |
| 12 | How do alerts get created? | Alerts are created when fraud score is at least 0.65 or rules fire. | Where are alerts stored? |
| 13 | What are risk bands? | Risk bands classify scores as low, medium, high, or critical. | Where is this shown in the UI? |
| 14 | What rules exist? | Sanctioned country, large transaction, velocity limit, and high-risk merchant amount. | Are rules a replacement for ML? |
| 15 | How does SHAP work here? | Tree SHAP is used when the XGBoost artifact loads; otherwise proxy contributions are returned. | Why is explainability important? |
| 16 | What is the LLM narrative? | A local Ollama-backed narrative or fallback template explains the alert in analyst language. | Why disable inline LLM in the light demo? |
| 17 | How is compliance handled? | Through sanctions screening, watchlist ingestion, SAR export, India STR-style reports, validation, and audit verification. | What is still needed for production compliance? |
| 18 | What is the audit chain? | Each audit record includes previous hash and entry hash, verified with SHA-256. | What actions are audited? |
| 19 | What is the DLQ? | A dead-letter queue captures invalid or failed stream messages. | How can messages be retried? |
| 20 | How is model governance represented? | Model versions are stored with lifecycle statuses such as draft, validated, approved, deployed, and retired. | Is it a full registry? |
| 21 | What does `/models/status` show? | Loaded artifact status, model mode, GNN scaffold note, and drift detection note. | How would you expose more metrics? |
| 22 | Is there a GNN? | A PyTorch Geometric scaffold exists; the status says it must be trained and validated before live blocking. | How would you productionize it? |
| 23 | Is drift detection implemented? | PSI demo code/status exists, but production feedback loops and retraining workflow remain future work. | What data is needed for drift? |
| 24 | How does auth work? | API key guard and bearer token support exist, with seeded users and roles. | What would you add for enterprise auth? |
| 25 | What roles exist? | Analyst, supervisor, auditor, and admin. | Which pages are role restricted? |
| 26 | What is the demo endpoint? | `/demo/generate?fraud_ring=true` creates a risky synthetic transaction and warmup graph context. | Why is it useful? |
| 27 | What is the light demo stack? | Postgres, Redis, API, and frontend with Kafka disabled for laptop-friendly demonstration. | When would you run the full stack? |
| 28 | What is the full stack? | Kafka, Zookeeper, Redis, PostgreSQL, Neo4j, MinIO, Ollama, API, consumer, generator, frontend, Prometheus, Grafana, ELK. | What services are optional? |
| 29 | What does Prometheus monitor? | API metrics exposed at `/metrics`, including transaction counter. | How would you add latency metrics? |
| 30 | What is Grafana used for? | Dashboard visualization over Prometheus metrics. | Are dashboards fully customized? |
| 31 | What is Kibana used for? | Searching logs from the ELK stack. | How does Logstash fit? |
| 32 | What is MinIO used for? | Local S3-compatible storage for model artifacts and deployment assets. | How would this map to cloud? |
| 33 | What Kubernetes assets exist? | Namespace, API/frontend deployments, stream consumer, generator, secrets example, CronJob, Helm chart. | Are they production-validated? |
| 34 | What does CI do? | Ruff, mypy, Bandit, training artifact generation, pytest, model regression tests, and frontend build. | What is missing from CI? |
| 35 | How is schema validation handled? | Kafka transaction messages are validated against schema logic, and a JSON schema contract exists in docs. | Would you add Schema Registry? |
| 36 | How are transactions partitioned? | Documentation states transactions are keyed by `account_id`, and tests cover partitioning. | Why partition by account? |
| 37 | What are the strongest implemented features? | End-to-end alert workflow, scoring, explanations, graph context, compliance drafts, audit logs, DLQ, and CI. | Which feature would you improve first? |
| 38 | What are current limitations? | Demo credentials, no SSO, official-feed operations need hardening, Kubernetes needs real-cluster validation, and cloud load testing is pending. | How would you address them? |
| 39 | How would this scale for a bank? | Run multiple API and consumer replicas, managed Kafka, managed Postgres/Redis/Neo4j, object storage, observability, and tested Kubernetes autoscaling. | What bottleneck would you test first? |
| 40 | How would you explain this in one sentence? | It turns transactions into explainable fraud alerts with graph context, analyst workflow, and compliance evidence. | What makes it different from a model demo? |

## 7. Client Questions: 20 Professional Answers

| # | Client Question | Professional Answer |
|---:|---|---|
| 1 | Why Kafka? | Kafka supports real-time event ingestion and decouples transaction producers from scoring consumers. In this project it is implemented for transaction streaming, feature output, alerts, and DLQ handling. |
| 2 | Why Neo4j? | Neo4j helps identify relationship risk, such as accounts sharing devices, IPs, merchants, or beneficiaries. That is useful for fraud rings. |
| 3 | Why Redis? | Redis provides low-latency velocity and reuse counters, which are important for real-time fraud decisions. |
| 4 | Why PostgreSQL? | PostgreSQL stores durable operational records: transactions, alerts, audit logs, users, reports, DLQ messages, watchlists, and model versions. |
| 5 | Why FastAPI? | FastAPI gives typed request validation, clean endpoint structure, and built-in Swagger documentation for integration review. |
| 6 | Why React? | React provides an interactive analyst console for alert review, investigation, graph context, compliance actions, and monitoring. |
| 7 | How is ML integrated? | The backend builds feature vectors and scores them through an ensemble service that loads local model artifacts when available. |
| 8 | What happens when models are unavailable? | The ensemble has deterministic fallback scoring so the demo remains functional. Production should use validated artifacts. |
| 9 | How are explanations generated? | SHAP TreeExplainer is used for the XGBoost artifact when available; otherwise proxy contributions are returned. |
| 10 | What does the LLM do? | It generates analyst-friendly narratives from explanation and graph data, with a local fallback if Ollama is unavailable. |
| 11 | How does this scale? | Scale API and stream consumers horizontally, use managed Kafka/Redis/Postgres/Neo4j, add autoscaling, and validate throughput in cloud staging. |
| 12 | Is this production ready? | It is demo and pilot ready, not fully bank-production ready. Production needs managed secrets, SSO, official feed operations, cloud load testing, and formal reviews. |
| 13 | How are failed messages handled? | Invalid or failed stream messages are persisted as dead letters and can be replayed through a controlled endpoint. |
| 14 | How is compliance supported? | The project includes watchlists, sanctions screening, SAR XML export, India STR-style report generation, validation, and audit verification. |
| 15 | Are audit logs tamper-evident? | Yes, audit records are hash-linked using SHA-256 and can be verified through an endpoint. |
| 16 | What monitoring exists? | The API exposes Prometheus metrics, and compose includes Prometheus, Grafana, and ELK services. |
| 17 | Why Docker? | Docker Compose makes local setup reproducible and supports both light demo and full-stack profiles. |
| 18 | Why Kubernetes? | Kubernetes manifests and Helm chart show the path to production-style deployment and scaling. They still need real-cluster validation. |
| 19 | What is MinIO for? | MinIO provides S3-compatible local object storage for model artifacts and related assets. |
| 20 | What would be the next production step? | Replace demo secrets, add SSO/OIDC, validate official watchlist feeds, run cloud load tests, harden Kubernetes, and complete security/compliance review. |

## 8. Repository Review and Suggested Improvements

### README

- Fix encoding issues in headings and emojis that currently render as corrupted characters.
- Update screenshot links to match actual files in `docs/screenshots`; current README references names like `dashboard.png`, but the repository contains longer screenshot filenames.
- Add a short "Honest Status" section: demo-ready, pilot-ready, production gaps.
- Add a one-command light demo start using `docker-compose.demo.yml`.
- Add demo credentials and ports in a table.

### Folder Structure

- Current structure is understandable: `backend`, `frontend`, `streaming`, `ml`, `graph`, `compliance`, `infra`, `monitoring`, `training`, `tests`, `docs`.
- Consider moving archived root notes further away from primary docs, for example `docs/archive/old-reports/`, so recruiters see the polished docs first.
- Add `docs/demo/` for this script, screenshots, and recording checklist.

### Documentation

- Expand `docs/api/openapi.md`; it currently only says where to open Swagger/ReDoc/schema.
- Add a real endpoint table with method, path, purpose, auth, and demo usage.
- Add a "Feature Status Matrix" marking implemented, fallback, scaffold, and production pending.
- Add deployment mode docs: light demo, full local stack, Kubernetes scaffold.

### Architecture

- The Mermaid architecture is useful. Add a rendered PNG for GitHub viewers and recruiters.
- Add sequence diagram for the end-to-end transaction flow.
- Add separate diagrams for streaming path, compliance path, and model governance path.

### Screenshots

- Rename screenshots with consistent lowercase names, for example `dashboard.png`, `swagger-ui.png`, `grafana.png`, `kibana.png`, `neo4j-graph.png`, `minio-registry.png`.
- Update README links after renaming.
- Add screenshots for Alert Queue, Investigation Workspace, Compliance Reports, DLQ Monitoring, Model Governance, and Pilot Readiness.

### Demo Video

- Record a three-minute version using the timeline above.
- Record a longer eight-minute technical version for interviews.
- Keep a short caption: "Production-style portfolio demo; not a live bank deployment."

### Portfolio Presentation

- Lead with business workflow, then architecture, then technical depth.
- Show the live dashboard before deep backend details.
- Include "what I would productionize next" to build trust.

### Recruiter Appeal

- Add a top-level "What this demonstrates" section: backend engineering, data engineering, ML engineering, MLOps, compliance-aware design, cloud-native deployment, and frontend product workflow.
- Add a polished GIF or short video link near the top of README.
- Add test/CI status badge after CI is green in GitHub.

### Technical Improvements

- Add more Prometheus metrics: scoring latency, alert count, DLQ count, model mode, Kafka publish failures.
- Add structured JSON logging from API and consumer.
- Add OpenAPI examples for transaction and compliance payloads.
- Add Docker health notes for each optional profile.
- Add production Helm values for resource requests, limits, probes, and autoscaling after cluster testing.

## 9. Accuracy Notes

- Kafka, Neo4j, MinIO, Ollama, Prometheus, Grafana, and ELK exist in `docker-compose.yml`; the light demo override disables Kafka and LLM inline generation for a faster local demo.
- ML artifacts exist in `training/model_registry`, and the scorer has fallback logic if artifacts are missing.
- SHAP is implemented with TreeExplainer plus proxy fallback.
- GNN and drift detection are present as scaffold/demo status items, not production decision engines.
- Kubernetes and Helm files exist, but the repository documents that real production validation is still pending.
- GitHub Actions CI exists; the blue-green job is currently a placeholder echo step.
- Compliance features are implemented for demo/pilot workflows; official-feed operations and regulator-grade validation need production hardening.
