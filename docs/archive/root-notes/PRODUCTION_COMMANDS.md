# Production Commands Reference

## Quick Alias (Add to PowerShell Profile)
```powershell
Set-Alias -Name dcf -Value { & docker compose -f "C:\Fraud detection\fraud-detection-system\docker-compose.yml" @args }
```

Then use: `dcf ps` instead of full path

---

## Essential Commands

### Start/Stop
```powershell
# Start everything
dcf up -d --build

# Stop (keep data)
dcf down

# Stop and delete data
dcf down -v

# Restart specific service
dcf restart api
```

### Status Checks
```powershell
# All services status
dcf ps

# Specific service logs
dcf logs -f api
dcf logs -f stream-consumer
dcf logs -f postgres

# All logs
dcf logs -f

# Health check
dcf exec api python -c "import requests; print(requests.get('http://localhost:8000/health').json())"
```

### Generate Transactions
```powershell
# Generate 1,000 transactions/sec for 30 seconds (10% fraud)
dcf exec api python -m streaming.transaction_generator.generator --rate 1000 --seconds 30 --fraud-ratio 0.1

# High volume test (5,000 TPS)
dcf exec api python -m streaming.transaction_generator.generator --rate 5000 --seconds 60 --fraud-ratio 0.05

# Stress test (10,000 TPS)
dcf exec api python -m streaming.transaction_generator.generator --rate 10000 --seconds 30 --fraud-ratio 0.2
```

### Query Data
```powershell
# Count alerts
dcf exec postgres psql -U fraud -d fraud -c "SELECT COUNT(*) FROM alerts;"

# View recent alerts
dcf exec postgres psql -U fraud -d fraud -c "SELECT transaction_id, score, risk_band FROM alerts ORDER BY created_at DESC LIMIT 10;"

# Audit logs count
dcf exec postgres psql -U fraud -d fraud -c "SELECT COUNT(*) FROM audit_logs;"

# System statistics
dcf exec postgres psql -U fraud -d fraud -c "
SELECT 
  (SELECT COUNT(*) FROM alerts) as total_alerts,
  (SELECT AVG(score) FROM alerts) as avg_fraud_score,
  (SELECT COUNT(DISTINCT account_id) FROM alerts) as unique_accounts
FROM alerts LIMIT 1;
"
```

### Run Tests
```powershell
# Unit tests
dcf exec api pytest tests/unit -v

# Integration tests
dcf exec api pytest tests/integration -v

# Load testing
dcf exec api locust -f tests/load/locustfile.py --host http://localhost:8000

# Code quality
dcf exec api ruff check backend streaming graph ml
dcf exec api mypy backend
dcf exec api bandit -r backend -x tests
```

### Dashboard URLs
```
Frontend Dashboard:  http://localhost:5173
Grafana:            http://localhost:3000       (admin/admin)
Neo4j:              http://localhost:7474       (neo4j/fraud_graph_password)
API Docs:           http://localhost:8000/docs
Kibana:             http://localhost:5601
Prometheus:         http://localhost:9090
MinIO:              http://localhost:9001       (fraudadmin/fraudadmin123)
```

### Backup Data
```powershell
# Backup alerts
dcf exec postgres psql -U fraud -d fraud -c "\COPY alerts TO '/tmp/alerts.csv' WITH CSV HEADER"
dcf cp fraud-detection-system-postgres-1:/tmp/alerts.csv ./alerts_backup.csv

# Backup audit logs
dcf exec postgres psql -U fraud -d fraud -c "\COPY audit_logs TO '/tmp/audit.csv' WITH CSV HEADER"
dcf cp fraud-detection-system-postgres-1:/tmp/audit.csv ./audit_logs_backup.csv

# Export all logs
dcf logs > system_logs.txt
```

### Troubleshooting
```powershell
# Check disk space
docker system df

# View resource usage
dcf stats

# Clean up unused resources
docker system prune -a

# Rebuild images
dcf build --no-cache

# Reset everything
dcf down -v --rmi all
dcf up -d --build
```

---

## Common Workflows

### Quick Start
```powershell
cd "C:\Fraud detection\fraud-detection-system"
dcf up -d --build
Start-Sleep -Seconds 30
dcf ps
```

### Full Test Run
```powershell
# Start
dcf up -d --build
Start-Sleep -Seconds 30

# Generate data
dcf exec api python -m streaming.transaction_generator.generator --rate 5000 --seconds 30 --fraud-ratio 0.1

# Check results
dcf exec postgres psql -U fraud -d fraud -c "SELECT COUNT(*) FROM alerts;"

# View dashboards
start http://localhost:5173
start http://localhost:3000
```

### Production Deployment
```powershell
# 1. Stop current
dcf down

# 2. Backup
dcf exec postgres psql -U fraud -d fraud -c "\COPY alerts TO '/tmp/alerts.csv' WITH CSV HEADER"
dcf cp fraud-detection-system-postgres-1:/tmp/alerts.csv ./alerts_backup.csv

# 3. Update code
# (git pull or copy new files)

# 4. Rebuild
dcf up -d --build

# 5. Verify
dcf ps
dcf logs -f api
```

### Performance Testing
```powershell
# Generate high volume
dcf exec api python -m streaming.transaction_generator.generator --rate 10000 --seconds 120 --fraud-ratio 0.1

# Monitor metrics
start http://localhost:3000  # Watch dashboard

# Check performance
dcf exec postgres psql -U fraud -d fraud -c "
SELECT 
  AVG(score) as avg_score,
  COUNT(*) as total_alerts,
  AVG(EXTRACT(EPOCH FROM (now() - created_at))) as age_seconds
FROM alerts;
"
```

---

## Environment Variables
```powershell
# View/Edit .env
cat .env

# Key variables
DATABASE_URL=postgresql+psycopg://fraud:fraud_password@postgres:5432/fraud
REDIS_URL=redis://redis:6379/0
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
NEO4J_URI=bolt://neo4j:7687
OLLAMA_BASE_URL=http://ollama:11434
```

---

## Notes
- Always use full path or alias for docker compose commands
- All data persists between restarts (unless -v flag used)
- System takes ~30 seconds to fully start
- First transaction generation takes ~5-10 seconds to initialize

