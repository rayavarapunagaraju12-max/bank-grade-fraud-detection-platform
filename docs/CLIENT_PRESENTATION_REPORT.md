# Fraud Detection Platform - Client Presentation Report

## Executive Summary

This project is a production-style real-time fraud detection platform for financial transaction monitoring. It demonstrates the full analyst workflow: transaction ingestion, streaming feature engineering, graph enrichment, machine learning risk scoring, explainable AI output, alert investigation, compliance evidence, and operational monitoring.

The system is suitable for a client demo and architecture review. It is not presented as a fully deployed banking production system yet; production hardening still requires real credentials, managed secrets, formal model governance, real sanctions feeds, and environment-specific deployment controls.

Recommended readiness framing:

- Client demo readiness: 80-90%
- Production-style pilot readiness: 60-70%
- Bank-grade production readiness: 35-45%

The local laptop environment should be used to prove workflow and architecture, not final enterprise capacity. For the current i7/16 GB laptop setup, present local throughput as a moderate-load demo target, typically 100-300 TPS with focused services enabled. Higher throughput must be validated in cloud or staging with horizontal scaling.

## Business Problem

Financial institutions need to detect suspicious transactions quickly while giving analysts a clear reason for every alert. A useful fraud platform must do more than produce a score. It must also explain the risk, preserve evidence, support investigation, and create an audit trail for compliance review.

This project addresses those needs by combining:

- Real-time transaction ingestion
- Velocity and behavior features
- Entity graph relationship analysis
- Ensemble fraud scoring
- SHAP-style model explanation
- Analyst alert queue
- SAR draft generation
- Sanctions screening evidence
- Tamper-evident audit logs
- Monitoring through Prometheus and Grafana

## System Architecture

The platform has these main layers:

- Frontend: React, TypeScript, Tailwind, Recharts, Cytoscape.js
- Backend API: FastAPI, Pydantic, SQLAlchemy
- Streaming: Kafka producer and consumer
- Feature store: Redis sliding-window features
- Database: PostgreSQL for transactions, alerts, and audit logs
- Graph: Neo4j for account, device, IP, merchant, and beneficiary relationships
- Machine learning: Ensemble scorer with model artifact hooks and deterministic fallback
- Explainability: SHAP-style feature contribution output
- Compliance: audit verification, SAR generation, sanctions screening
- Monitoring: Prometheus, Grafana, ELK stack

## End-to-End Flow

1. A transaction is submitted through the API or Kafka stream.
2. The system stores the transaction record.
3. Kafka publishes the event for streaming consumers.
4. Redis computes recent activity features such as account velocity and device reuse.
5. Neo4j stores entity relationships and provides graph features.
6. The ensemble scorer calculates fraud risk.
7. Rule-based compliance checks run against transaction and feature evidence.
8. If the risk is high enough, an alert is stored in PostgreSQL.
9. A tamper-evident audit event is written.
10. The frontend shows the alert, explanation, transaction details, and graph context.

## Production Integration Work Completed

Recent improvements added during the production-integration pass:

- Shared alert persistence service used by both API and Kafka consumer paths.
- Kafka stream consumer now persists high-risk alerts to PostgreSQL.
- Stream consumer now uses PostgreSQL in Docker Compose instead of falling back to local SQLite.
- Compliance API endpoints added:
  - `GET /compliance/audit/verify`
  - `POST /compliance/sanctions/screen`
  - `POST /compliance/sar`
  - `POST /compliance/sar/export`
- Offline demo sanctions screening service restored.
- SAR generation typing fixed.
- Audit hash-chain typing fixed.
- Frontend client-facing labels cleaned for a more professional presentation.
- Safer local API host default changed to `127.0.0.1`; Docker still overrides to `0.0.0.0`.
- Unit and API contract tests added for compliance behavior.

## Explainability Story For Client

The platform is explainable at three levels:

- Model explanation: The score includes feature contributions such as transaction amount, velocity, device reuse, IP reuse, graph degree, and path to known fraud.
- Rule explanation: Compliance rules return the exact rule that fired, such as high-risk merchant, velocity limit, large transaction, or sanctioned country.
- Audit explanation: Every generated alert and SAR action is recorded with a hash-linked audit event so later tampering can be detected.

This gives analysts and reviewers a clear answer to: "Why was this transaction flagged?"

## Demo Script

Use this simple flow for the client. For a fuller step-by-step talk track, see `docs/CLIENT_DEMO_PLAYBOOK.md`.

1. Start the stack:

```powershell
docker compose up -d --build
```

2. Open the analyst dashboard:

```text
http://localhost:5173
```

3. Generate an AI fraud case from the frontend, or call:

```powershell
Invoke-RestMethod -Method Post "http://localhost:8000/demo/generate?fraud_ring=true"
```

4. Show the alert queue:

```text
http://localhost:5173
```

5. Show API docs:

```text
http://localhost:8000/docs
```

6. Verify audit integrity:

```powershell
Invoke-RestMethod "http://localhost:8000/compliance/audit/verify"
```

7. Demonstrate sanctions screening:

```powershell
Invoke-RestMethod -Method Post "http://localhost:8000/compliance/sanctions/screen" `
  -ContentType "application/json" `
  -Body '{"name":"Kim Jong Un","country":"KP"}'
```

8. Export a SAR XML draft from `/docs` or via the `/compliance/sar/export` endpoint.

9. Open the Pilot Readiness page in the frontend and explain what is demo ready, what is production hardening, and how the architecture scales beyond the laptop.

## Current Validation Status

The following checks pass:

- Ruff lint check
- Mypy type check
- Bandit security scan
- Unit tests and API contract tests
- Frontend production build
- Docker Compose configuration parsing

Known non-blocking warnings:

- Frontend bundle is larger than 500 kB because charts, graph visualization, icons, and analytics libraries are bundled together.
- Tests show third-party deprecation warnings from Matplotlib, SHAP, FastAPI startup events, and pytest cache permissions.
- Docker reports access denied for `C:\Users\nagar\.docker\config.json` on this machine, but Compose config still parses.

## Remaining Production Tasks

To move from demo-ready to bank-grade production, complete these items:

- Add authentication and role-based access control for analysts, admins, and auditors.
- Replace demo credentials with managed secrets.
- Add database migrations with Alembic.
- Add real OFAC, EU, UN, and UK HMT sanctions feed ingestion.
- Validate SAR XML against the official regulator schema used by the target market.
- Add model registry promotion controls and approval workflow.
- Add persisted trained model artifacts for XGBoost, Isolation Forest, and meta-learner.
- Add schema contracts for Kafka messages.
- Add dead-letter queues and retry policy for stream processing.
- Add full CI pipeline for backend, frontend, Docker, security, and integration tests.
- Add production Helm values with resource limits, probes, autoscaling, and secrets references.

## Honest Client Positioning

Recommended wording:

"This is a production-style fraud detection platform and working demo. It demonstrates the complete detection and investigation workflow, including streaming ingestion, graph enrichment, explainable scoring, compliance audit logs, SAR draft export, and analyst dashboard. Before real banking deployment, the remaining work is production hardening: authentication, managed secrets, official sanctions feeds, formal model governance, and environment-specific deployment controls."

Recommended performance wording:

"The laptop demo is intended for functional validation and moderate load testing, not final capacity certification. On this machine, we target 100-300 TPS for a focused demo. Production-scale targets such as 10k TPS require cloud deployment, horizontal scaling, and formal load testing."
