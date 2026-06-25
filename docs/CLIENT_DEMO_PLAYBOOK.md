# Client Demo Playbook

## Positioning

Use this wording at the start of the demo:

> This is a production-style fraud detection pilot. It demonstrates the complete detection and investigation workflow locally: transaction ingestion, streaming features, graph enrichment, fraud scoring, explainable alerts, compliance evidence, audit verification, and monitoring. A real bank production rollout would add hardened authentication, managed secrets, official sanctions feeds, model governance, cloud scaling, and formal security review.

Avoid saying the laptop proves 10k TPS. Say:

> The laptop demo is designed for functional validation and moderate load testing, usually around 100-300 TPS with the focused demo stack. The architecture is designed to scale further in cloud or staging after horizontal deployment and load testing.

## Demo Goal

The client should leave with three clear ideas:

- The platform detects risky transactions and explains why.
- Analysts get a usable investigation workflow, not just a model score.
- Compliance and audit evidence are built into the workflow.

## Recommended Demo Flow

1. Open the dashboard

For the smoother laptop demo, start the focused stack:

```powershell
docker compose -f docker-compose.yml -f docker-compose.demo.yml up -d --build postgres redis api frontend
```

This starts the client demo with API-key protection enabled and keeps heavier services optional.

```text
http://localhost:5173
```

Show the executive view: open alerts, fraud rate, risk distribution, and live transaction feed.

2. Generate a fraud case

Click `Generate AI Fraud Case`, or run:

```powershell
Invoke-RestMethod -Method Post "http://localhost:8000/demo/generate?fraud_ring=true"
```

Explain that this creates a risky transaction with shared device/IP behavior.

3. Show the alert queue

Open `Fraud Alert Queue`. Point out:

- Risk-ranked alerts
- Fraud score
- Risk band
- Investigation status

4. Show investigation details

Open `Investigation Workspace`. Explain:

- Transaction amount and risk score
- SHAP-style feature reasons
- AI narrative for analyst review
- Recommended next action

5. Show graph context

Open `Graph Visualization`. Explain:

- Account, device, IP, and merchant relationships
- Shared identifiers that indicate possible fraud rings
- Why graph context matters beyond single-transaction scoring

6. Show compliance evidence

Open `Compliance Reports`. Demonstrate:

- Watchlist refresh
- Sanctions screening
- India STR-style draft generation

Then verify the audit chain:

```powershell
Invoke-RestMethod "http://localhost:8000/compliance/audit/verify"
```

7. Show pilot readiness

Open `Pilot Readiness`. This is the trust-building screen. Explain:

- What is demo ready
- What is planned for production hardening
- Laptop TPS versus cloud validation
- Roadmap from demo to pilot to production

## Laptop Demo Recommendation

Your laptop:

- Intel Core i7-1360P
- 16 GB RAM
- Enough storage for the project

Recommended demo stack:

- API
- Frontend
- PostgreSQL
- Redis
- Kafka if showing streaming
- Neo4j if showing graph relationships

Avoid running these during a performance-focused demo unless needed:

- Ollama for every transaction
- Elasticsearch
- Logstash
- Kibana
- Heavy Grafana dashboards

## Safe Capacity Statement

Use this table in discussion:

| Environment | Safe Statement |
|---|---:|
| Laptop full demo | 100-300 TPS |
| Optimized laptop mode | 300-700 TPS |
| Cloud pilot target | 1k-5k TPS |
| Production architecture target | 10k TPS after cloud validation |

## Production-Style Controls Added

The demo now includes several production-style controls:

- API key protection can be enabled with `ENABLE_API_KEY_AUTH=true`.
- The frontend sends `VITE_API_KEY=demo-client-key` for protected demo calls.
- Full LLM narratives are not generated inline by default; the fast response returns the score and queues narrative work.
- `/production/readiness` exposes honest demo, pilot, and production readiness status.
- `/models/status` exposes model artifact status and separates trained artifacts from demo/scaffold components.
- `docker-compose.demo.yml` provides a lighter laptop-friendly demo profile.
- Alembic migration scaffolding is available for database schema management.

Useful checks:

```powershell
Invoke-RestMethod "http://localhost:8000/production/readiness"
Invoke-RestMethod "http://localhost:8000/models/status" -Headers @{"X-API-Key"="demo-client-key"}
```

## Client Questions And Answers

### Is this production ready?

It is demo and pilot ready. It is not being represented as a fully deployed bank production system yet. The next steps are security hardening, official data feeds, model governance, CI/CD, and cloud load testing.

### Why not prove 10k TPS on the laptop?

A laptop Docker Compose environment is not the right place to prove enterprise throughput. The laptop proves workflow and architecture. Throughput is validated in staging or cloud with multiple API instances, stream consumers, managed databases, and monitoring.

### What makes this more than a model demo?

The system includes the operational workflow around the model: alerts, explanations, graph context, compliance reports, audit logs, monitoring, and investigation screens.

### What is the fastest path to production?

Start with a controlled pilot:

1. Add authentication and role-based access.
2. Replace demo credentials with managed secrets.
3. Add database migrations.
4. Add CI/CD checks.
5. Move full explanations and LLM narratives to background workers.
6. Validate load in cloud staging.
7. Complete security and compliance review.

## Final Demo Close

Use this closing line:

> The strength of this platform is that it connects detection, explanation, investigation, and compliance in one workflow. The demo proves the business flow today, and the roadmap shows exactly how to harden it for production.
