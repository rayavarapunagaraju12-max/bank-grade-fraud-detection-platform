 # 🛡️ Bank-Grade Real-Time Fraud Detection Platform using with AI

A production-style real-time financial fraud detection platform built using Apache Kafka, FastAPI, Neo4j, Redis, PostgreSQL, Machine Learning, Explainable AI, and Graph Analytics.

This platform simulates how modern banks and fintech companies detect fraudulent transactions in real time by combining streaming data pipelines, graph-based fraud detection, explainable machine learning, compliance workflows, and analyst investigation tools.

---

## 🚀 Key Features

### Real-Time Transaction Processing

* High-throughput transaction ingestion
* Apache Kafka event streaming
* Real-time fraud scoring pipeline
* Idempotent event processing
* Dead Letter Queue (DLQ) support

### Machine Learning Fraud Detection

* XGBoost fraud classification
* Isolation Forest anomaly detection
* Model artifact registry
* Automated model loading
* Fraud risk scoring API

### Graph-Based Fraud Intelligence

* Neo4j knowledge graph
* Entity relationship mapping
* Fraud ring detection
* Account-device-IP correlation
* Known fraud account labeling

### Explainable AI

* SHAP feature importance explanations
* Human-readable fraud reasoning
* Investigation-ready evidence generation

### Fraud Analyst Console

* React-based dashboard
* Alert queue management
* Case investigation workflow
* Risk monitoring
* Historical fraud analysis

### Compliance & Governance

* Audit logging
* Alert persistence
* Evidence tracking
* Model governance
* Compliance workflows

### Production Engineering

* Docker deployment
* Kubernetes manifests
* Health checks
* Prometheus monitoring
* CI/CD automation
* Security scanning

---

# 🏗 System Architecture

Transaction Sources

↓

Apache Kafka

↓

Stream Processing

↓

Feature Engineering

↓

Redis Feature Store

↓

Fraud Scoring Engine

(XGBoost + Anomaly Detection)

↓

Neo4j Graph Analytics

↓

SHAP Explainability

↓

Alert Generation

↓

Fraud Analyst Dashboard

↓

Compliance & Audit Trail

---
## Screenshots

### FraudOps Analyst Dashboard

Real-time fraud monitoring dashboard with alert queue, investigations, graph visualization, compliance reports, and model governance.

![FraudOps Dashboard](docs/screenshots/dashboard.png)

---

### API Documentation

Interactive OpenAPI documentation for transaction ingestion, authentication, alert management, and model governance APIs.

![Swagger API](docs/screenshots/swagger-api.png)

---

### Grafana Monitoring

Operational monitoring dashboard for application metrics, transaction throughput, and system health.

![Grafana](docs/screenshots/grafana.png)

---

### Kibana Log Analytics

Centralized log management and search for fraud platform services.

![Kibana](docs/screenshots/kibana.png)

---

### Model Artifact Registry

MinIO object storage used for model artifacts, governance records, and deployment assets.

![MinIO](docs/screenshots/minio.png)

# ⚙️ Technology Stack

## Backend

* Python 3.12
* FastAPI
* Uvicorn
* Pydantic
* SQLAlchemy

## Streaming

* Apache Kafka
* Confluent Kafka Client

## Databases

* PostgreSQL
* Redis
* Neo4j

## Machine Learning

* Scikit-Learn
* XGBoost
* PyTorch
* PyTorch Geometric
* SHAP

## Frontend

* React
* TypeScript

## Infrastructure

* Docker
* Kubernetes
* Helm

## Monitoring

* Prometheus

## Storage

* MinIO

---

# 📊 Core Business Capabilities

✅ Real-Time Fraud Detection

✅ Transaction Risk Scoring

✅ Fraud Ring Identification

✅ Graph Relationship Analysis

✅ Explainable AI Decisions

✅ Compliance Evidence Tracking

✅ Investigation Workflow Management

✅ Audit Trail Generation

---

# 📁 Project Structure

backend/

* Fraud scoring APIs
* Alert management
* Compliance workflows

streaming/

* Kafka producer
* Kafka consumer
* Event processing

training/

* Model training pipelines
* Artifact generation
* Model registry

frontend/

* Analyst dashboard
* Alert management UI
* Investigation views

graph/

* Neo4j integrations
* Entity relationship analysis

compliance/

* Audit logging
* Governance workflows

infra/

* Docker deployment
* Kubernetes manifests
* Helm charts

tests/

* Unit tests
* Integration tests
* Model regression tests

---

# 🔌 Main API Endpoints

GET /health

GET /ready

POST /auth/token

POST /transactions

GET /dashboard/summary

GET /alerts

GET /models/status

POST /demo/generate

---

# 🧪 Quality & Testing

Ruff Code Quality

MyPy Type Checking

Bandit Security Scanning

Pytest Unit Testing

Integration Testing

Model Regression Testing

Frontend Build Validation

---

# 📈 Project Highlights

* Real-time fraud scoring pipeline
* Event-driven architecture
* Graph-powered fraud investigation
* Explainable AI decisions
* Compliance-ready audit trails
* Production-style deployment architecture
* End-to-end fraud investigation workflow

---

# 🎯 Portfolio Value

This project demonstrates practical experience in:

* Data Engineering
* Machine Learning Engineering
* MLOps
* Streaming Systems
* Fraud Analytics
* Distributed Systems
* Graph Analytics
* Backend Development
* Cloud-Native Architecture

---

# 🖥️ Screenshots

Add screenshots inside:

docs/screenshots/

Recommended screenshots:

* Dashboard
* Alert Queue
* Fraud Investigation
* Neo4j Graph View
* Model Governance
* Monitoring Dashboard
* Compliance Reports

---

# 🚀 Quick Start

```bash
python -m training.pipelines.train_artifacts

python -m pytest tests/unit tests/model_regression

cd frontend
npm run build
```

Docker:

```bash
copy .env.example .env

docker compose up --build
```

---

# 📜 License

This project is intended for educational, portfolio, and research purposes demonstrating modern fraud detection architecture and machine learning engineering practices.
