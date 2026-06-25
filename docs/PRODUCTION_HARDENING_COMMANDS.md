# Production-Hardening Demo Commands

Run commands from the repository root.

## Frontend Chunked Build

```powershell
cd frontend
npm run build
cd ..
```

Expected output includes multiple JavaScript chunks such as `vendor-react`, `vendor-charts`, `vendor-graph`, and `vendor-icons`.

## Kafka Contract Validation

```powershell
python -m pytest tests/unit/test_kafka_schema.py -v
```

Contract artifact:

```text
docs/contracts/kafka-transaction.schema.json
```

Runtime validation is performed by:

```text
streaming/schemas/transactions.py
```

## Official Watchlist Refresh Job

Run locally inside the API container:

```powershell
docker compose exec api python -m compliance.watchlist_ingestion.refresh_job
```

Kubernetes CronJob scaffold:

```text
infra/kubernetes/watchlist-refresh-cronjob.yaml
```

## Helm Production Values

Render with production-style values:

```powershell
helm template fraud infra/helm/fraud-detection -f infra/helm/fraud-detection/values.production.example.yaml
```

The Helm chart expects sensitive values in the Kubernetes Secret named `fraud-secrets`.

## Kubernetes Secret Example

```powershell
kubectl apply -f infra/kubernetes/secrets.example.yaml
```

Replace every placeholder before using it outside a local demo.
