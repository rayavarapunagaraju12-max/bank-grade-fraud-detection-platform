# Bank-Grade Portfolio Readiness

This project is positioned as a production-style fraud detection platform suitable for a senior portfolio demo and pilot architecture review.

## Current Readiness

| Readiness area | Status |
|---|---:|
| Client demo | 95-100% |
| Production-style pilot | 80-90% |
| Bank-grade production portfolio | 65-75% |

The system should not be described as fully deployed bank production. Real production still requires cloud secrets, SSO/OIDC, official feed operations, formal security review, regulator sign-off, and cloud load testing.

## Bank-Grade Controls Added

- API key and bearer-token guardrails.
- Role-based analyst, supervisor, auditor, and admin paths.
- Audited alert investigation lifecycle.
- Alert assignment, reviewer, decision, notes, and resolution timestamps.
- Dead-letter queue capture and controlled replay.
- DLQ retry count and replay audit trail.
- Kafka transaction schema validation before publish and consume.
- Kafka transaction JSON schema contract artifact in `docs/contracts/`.
- Analyst alert workflow controls in the investigation UI.
- Model registry lifecycle: draft, validated, approved, deployed, retired.
- Watchlist ingestion status and official-feed refresh path.
- Kubernetes CronJob scaffold for official watchlist refresh.
- Alembic migration baseline and bank-grade workflow migration.
- Helm chart uses Kubernetes secret references for production credentials.
- Frontend bundle is split into React, chart, graph, icon, and shared vendor chunks.
- CI checks for linting, typing, security scanning, backend tests, model regression, and frontend build.

## Honest Production Gaps

- Replace demo credentials with managed secrets and rotation.
- Integrate SSO/OIDC with enterprise identity provider.
- Add scheduled official sanctions feed refresh with monitoring and alerting.
- Add external Kafka schema registry and compatibility gates.
- Validate Kubernetes resources, probes, autoscaling, CronJobs, and secrets in a real cluster.
- Run cloud/staging load tests for 1k-5k TPS pilot targets and 10k TPS architecture targets.
- Complete formal security and compliance review.

## Interview Positioning

Use this wording:

> This is a bank-grade portfolio implementation of a real-time fraud detection platform. It demonstrates transaction ingestion, streaming features, explainable scoring, graph enrichment, alert investigation, compliance evidence, audit logs, DLQ handling, model governance, and CI. It is demo and pilot ready. Full bank production would require managed cloud secrets, SSO, official feed operations, cloud load testing, and formal security/compliance approval.
