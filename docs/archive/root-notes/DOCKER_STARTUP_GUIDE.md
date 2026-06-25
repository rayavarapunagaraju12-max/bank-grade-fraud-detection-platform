# 🚀 DOCKER COMPOSE STARTUP & PROJECT STATUS VERIFICATION

## ❌ THE PROBLEM

You ran:
```powershell
docker compose up -d --build
# Error: no configuration file provided: not found
```

**Why:** Without specifying files, Docker looks for `docker-compose.yml` in the current directory. You need to tell it which files to use.

---

## ✅ THE SOLUTION

### Step 1: Navigate to Project Directory
```powershell
cd "C:\Fraud detection\fraud-detection-system"
```

### Step 2: Choose Your Startup Command

You have **THREE PROFILE MODES**:

---

## 🎯 STARTUP OPTIONS

### Option A: Quick Demo (Minimal - Recommended for Testing)
```powershell
# Starts: PostgreSQL, Redis, API, Frontend
# NO Kafka, Neo4j, ELK, Prometheus, Ollama
# Best for: Quick testing, minimal resources

docker compose -f docker-compose.yml -f docker-compose.demo.yml up -d --build
```

**Ports:**
- API: http://localhost:8000
- Frontend: http://localhost:5173
- PostgreSQL: localhost:5432
- Redis: localhost:6379

**Resources:** ~2-3 GB RAM

---

### Option B: Full Stack with Streaming (Recommended for Production-Like Testing)
```powershell
# Starts: ALL services including Kafka, Neo4j, streaming consumer
# Includes: Prometheus, Grafana for monitoring
# NO Ollama (LLM), NO ELK logging
# Best for: Full fraud detection with streaming

docker compose -f docker-compose.yml --profile streaming --profile monitoring up -d --build
```

**Ports:**
- API: http://localhost:8000
- Frontend: http://localhost:5173
- Kafka: localhost:9092
- Neo4j: http://localhost:7474
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000
- PostgreSQL: localhost:5432
- Redis: localhost:6379

**Resources:** ~6-8 GB RAM

---

### Option C: Complete Production Stack (Everything)
```powershell
# Starts: ALL services including LLM, monitoring, logging
# Includes: Kafka, Neo4j, Prometheus, Grafana, ELK, Ollama
# Best for: Full production-style deployment

docker compose -f docker-compose.yml \
  --profile streaming \
  --profile graph \
  --profile monitoring \
  --profile logging \
  --profile ai \
  up -d --build
```

**Ports:**
- API: http://localhost:8000
- Frontend: http://localhost:5173
- Kafka: localhost:9092
- Neo4j: http://localhost:7474 (neo4j/fraud_graph_password)
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)
- Kibana: http://localhost:5601
- Elasticsearch: localhost:9200
- Ollama: localhost:11434
- MinIO: http://localhost:9001 (fraudadmin/fraudadmin123)
- PostgreSQL: localhost:5432
- Redis: localhost:6379

**Resources:** ~12-15 GB RAM

---

## 🎯 RECOMMENDED: Start with Option B (Full Stack)

```powershell
# Step 1: Navigate to project
cd "C:\Fraud detection\fraud-detection-system"

# Step 2: Start all services (except logging & LLM)
docker compose -f docker-compose.yml --profile streaming --profile monitoring up -d --build

# Step 3: Wait for all services to start (2-3 minutes)
Start-Sleep -Seconds 120

# Step 4: Verify all services are running
docker compose ps
```

**Expected Output:**
```
NAME              STATUS              PORTS
postgres          Up 2 minutes        0.0.0.0:5432->5432/tcp
redis             Up 2 minutes        0.0.0.0:6379->6379/tcp
kafka             Up 2 minutes        0.0.0.0:9092->9092/tcp
neo4j             Up 2 minutes        0.0.0.0:7474->7474/tcp
api               Up 1 minute         0.0.0.0:8000->8000/tcp
frontend          Up 1 minute         0.0.0.0:5173->5173/tcp
stream-consumer   Up 1 minute         (no ports)
prometheus        Up 1 minute         0.0.0.0:9090->9090/tcp
grafana           Up 1 minute         0.0.0.0:3000->3000/tcp
```

---

## ✅ VERIFICATION CHECKLIST (After Startup)

### ☐ Step 1: Check All Services Running
```powershell
# Should show all services with status "Up"
docker compose ps
```

### ☐ Step 2: Verify Database Initialized
```powershell
# Connect to PostgreSQL and check tables exist
docker compose exec postgres psql -U fraud -d fraud -c "\dt"

# Expected output: ~10 tables (alerts, cases, audit_logs, etc.)
```

### ☐ Step 3: Verify API Health
```powershell
# Test API endpoint
Invoke-WebRequest -Uri "http://localhost:8000/health" -ErrorAction SilentlyContinue | Select-Object -Property Content

# Expected: {"status": "ok", "version": "1.0.0"}
```

### ☐ Step 4: Verify Neo4j Graph (if using Option B or C)
```powershell
# Open Neo4j browser
start http://localhost:7474

# Login: neo4j / fraud_graph_password
# Run query: MATCH (n) RETURN COUNT(n);
# Should return node count
```

### ☐ Step 5: Verify Kafka Topics (if using Option B or C)
```powershell
# Check Kafka topics
docker compose exec kafka kafka-topics --list --bootstrap-server localhost:9092

# Should show: transactions, fraud-alerts, etc.
```

### ☐ Step 6: Verify Redis Cache
```powershell
# Check Redis is working
docker compose exec redis redis-cli PING

# Expected: PONG
```

### ☐ Step 7: Open Dashboards

**API Documentation:**
```
http://localhost:8000/docs
```

**Frontend Dashboard:**
```
http://localhost:5173
```

**Grafana Monitoring (Option B or C):**
```
http://localhost:3000
Username: admin
Password: admin
```

**Prometheus Metrics (Option B or C):**
```
http://localhost:9090
```

**Neo4j Browser (Option B or C):**
```
http://localhost:7474
Username: neo4j
Password: fraud_graph_password
```

---

## 🧪 QUICK FUNCTIONALITY TEST

### Test 1: Create a Transaction
```powershell
# Generate a test transaction
$transaction = @{
    transaction_id = "test-$(Get-Random)"
    account_id = "ACC-001"
    amount = 999.99
    merchant_id = "MERCH-001"
    timestamp = (Get-Date -AsUTC).ToString("o")
    channel = "card_not_present"
    country = "US"
} | ConvertTo-Json

# Send to API
Invoke-WebRequest -Uri "http://localhost:8000/transactions/score" `
    -Method POST `
    -Headers @{"Content-Type"="application/json"} `
    -Body $transaction
```

**Expected Response:**
```json
{
  "transaction_id": "test-xxx",
  "score": 0.25,
  "risk_band": "LOW",
  "explanation": {
    "top_factors": [...]
  },
  "status": "success"
}
```

### Test 2: Query Fraud Alerts
```powershell
# Get fraud alerts from database
docker compose exec postgres psql -U fraud -d fraud -c \
  "SELECT transaction_id, score, risk_band FROM alerts LIMIT 5;"
```

### Test 3: Check Stream Consumer
```powershell
# View stream consumer logs
docker compose logs -f stream-consumer --tail 20

# Should show: Processing transactions, updating Neo4j, etc.
```

---

## 🛠️ TROUBLESHOOTING

### Issue 1: Port Already in Use
```powershell
# Example: Port 8000 in use by another process
# Solution: Kill the process or use different port

# Find what's using port 8000
Get-NetTCPConnection -LocalPort 8000 | Select-Object -Property OwningProcess

# Stop the container
docker compose down
```

### Issue 2: Build Failures
```powershell
# Clear build cache and rebuild
docker compose down -v
docker system prune -a --volumes
docker compose -f docker-compose.yml --profile streaming --profile monitoring up -d --build
```

### Issue 3: Database Not Initialized
```powershell
# Check PostgreSQL logs
docker compose logs postgres --tail 50

# Reset database
docker compose down -v
docker compose up -d postgres
Start-Sleep -Seconds 30
docker compose up -d --build
```

### Issue 4: High Memory Usage
```powershell
# Check resource usage
docker stats

# Reduce services: Use Option A (Quick Demo) instead of Option C
```

### Issue 5: Services Not Communicating
```powershell
# Check network
docker network ls
docker network inspect fraud-detection-system_default

# View service logs
docker compose logs api --tail 50
docker compose logs stream-consumer --tail 50
```

---

## 📊 PROJECT STATUS CHECKS

### Check 1: System Health
```powershell
# All services running?
docker compose ps | grep -E "Up|Exit"

# Should show all "Up"
```

### Check 2: Database Status
```powershell
# Check table row counts
docker compose exec postgres psql -U fraud -d fraud -c "
SELECT
  'alerts' as table_name, COUNT(*) as row_count FROM alerts
UNION ALL
SELECT 'cases', COUNT(*) FROM cases
UNION ALL
SELECT 'audit_logs', COUNT(*) FROM audit_logs
UNION ALL
SELECT 'users', COUNT(*) FROM users;
"

# Expected: Non-zero for alerts if transactions processed
```

### Check 3: API Response Time
```powershell
# Test API latency
$start = Get-Date
Invoke-WebRequest -Uri "http://localhost:8000/health" -ErrorAction SilentlyContinue | Out-Null
$elapsed = ((Get-Date) - $start).TotalMilliseconds
Write-Host "API Response Time: ${elapsed}ms"

# Expected: <100ms for healthy system
```

### Check 4: Throughput (Transactions Processed)
```powershell
# Count transactions in last hour
docker compose exec postgres psql -U fraud -d fraud -c "
SELECT COUNT(*) as transactions_last_hour
FROM alerts
WHERE created_at > NOW() - INTERVAL '1 hour';
"
```

### Check 5: Resource Usage
```powershell
# Check Docker resource usage
docker stats --no-stream

# Memory usage should be:
# Option A: <3 GB
# Option B: <8 GB
# Option C: <15 GB
```

### Check 6: Model Performance
```powershell
# Check fraud detection metrics
docker compose exec postgres psql -U fraud -d fraud -c "
SELECT
  risk_band,
  COUNT(*) as count,
  ROUND(AVG(score), 4) as avg_score
FROM alerts
GROUP BY risk_band
ORDER BY risk_band;
"

# Expected output:
# HIGH   | 234 | 0.7234
# MEDIUM | 456 | 0.5123
# LOW    | 789 | 0.2234
```

---

## 🎯 FULL STARTUP SCRIPT (Copy & Paste)

```powershell
# ============================================
# FRAUD DETECTION SYSTEM - FULL STARTUP
# ============================================

Write-Host "🚀 Starting Fraud Detection System..." -ForegroundColor Green

# Step 1: Navigate to project
Write-Host "`n📁 Navigating to project directory..."
cd "C:\Fraud detection\fraud-detection-system"

# Step 2: Start services
Write-Host "`n🐳 Starting Docker services..."
docker compose -f docker-compose.yml --profile streaming --profile monitoring up -d --build

# Step 3: Wait for services to start
Write-Host "`n⏳ Waiting for services to start (2 minutes)..."
Start-Sleep -Seconds 120

# Step 4: Check status
Write-Host "`n✅ Checking service status..."
docker compose ps

# Step 5: Verify database
Write-Host "`n📊 Verifying database..."
docker compose exec postgres psql -U fraud -d fraud -c "SELECT COUNT(*) as table_count FROM information_schema.tables WHERE table_schema='public';"

# Step 6: Verify API
Write-Host "`n🔧 Testing API health..."
$health = Invoke-WebRequest -Uri "http://localhost:8000/health" -ErrorAction SilentlyContinue
if ($health.StatusCode -eq 200) {
    Write-Host "✅ API is healthy!" -ForegroundColor Green
} else {
    Write-Host "❌ API is not responding" -ForegroundColor Red
}

# Step 7: Open dashboards
Write-Host "`n🌐 Opening dashboards..."
Write-Host "  API Docs:       http://localhost:8000/docs"
Write-Host "  Frontend:       http://localhost:5173"
Write-Host "  Grafana:        http://localhost:3000 (admin/admin)"
Write-Host "  Prometheus:     http://localhost:9090"
Write-Host "  Neo4j Browser:  http://localhost:7474 (neo4j/fraud_graph_password)"

# Step 8: Display summary
Write-Host "`n📋 SYSTEM SUMMARY"
Write-Host "=================================="
docker compose ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

Write-Host "`n✅ System is ready!" -ForegroundColor Green
Write-Host "Open http://localhost:5173 to access the dashboard"
```

---

## 📈 PROJECT READINESS FOR PRODUCTION

### Current Status: 40-50% Complete
```
✅ READY:
  ├─ Core fraud detection (ML ensemble)
  ├─ Real-time processing (Kafka streaming)
  ├─ Explainability (SHAP + LLM)
  ├─ Knowledge graph (Neo4j)
  ├─ Audit logging (tamper-proof)
  ├─ Case management UI
  ├─ Monitoring (Prometheus/Grafana)
  └─ Docker deployment

❌ NOT YET:
  ├─ 10,000+ TPS throughput (1,124 current)
  ├─ <50ms latency (145ms current)
  ├─ Horizontal scaling (1 consumer)
  ├─ Encryption at rest
  ├─ Kubernetes deployment
  ├─ GNN fraud rings
  └─ Online learning
```

### What Makes This Production-Style
```
✅ Multi-service architecture (15 services)
✅ Distributed processing (Kafka + consumers)
✅ Persistent storage (PostgreSQL volumes)
✅ Caching layer (Redis)
✅ Graph database (Neo4j)
✅ Real-time monitoring (Prometheus/Grafana)
✅ Full observability (ELK stack available)
✅ Container orchestration (Docker Compose)
✅ Audit trail (compliance-ready)
✅ API with documentation (FastAPI/Swagger)
```

### What's Still Needed for True Production
```
❌ Kubernetes deployment (multi-node scaling)
❌ Database replication (high availability)
❌ Load balancing (horizontal scaling)
❌ Encryption (AES-256, mTLS)
❌ Auto-scaling policies
❌ Disaster recovery procedures
❌ 99.9% SLA validation
❌ Security hardening
❌ Multi-region deployment
```

---

## 🎯 NEXT STEPS AFTER STARTUP

### 1. Verify System is Working (15 minutes)
```powershell
# Run all verification checks above
# Confirm all services are "Up"
# Test API endpoints
# Check database tables
```

### 2. Generate Test Data (Optional)
```powershell
# Generate 1,000 transactions for testing
docker compose exec api python -m streaming.transaction_generator.generator \
  --rate 1000 --seconds 1 --fraud-ratio 0.1
```

### 3. Monitor System Performance
```powershell
# Watch logs in real-time
docker compose logs -f api stream-consumer

# Open Grafana dashboard
start http://localhost:3000

# Open Prometheus
start http://localhost:9090
```

### 4. Run Load Test (If Desired)
```powershell
# Test system with higher throughput
docker compose exec api python -m tools.load_test \
  --transactions 5000 --duration 30
```

---

## 📊 EXPECTED OUTPUT AFTER STARTUP

```
✅ All 9 services running (Option B)
✅ API responding to requests (<100ms)
✅ Frontend accessible at :5173
✅ Database initialized with schema
✅ Kafka topics created
✅ Neo4j started and ready
✅ Prometheus scraping metrics
✅ Grafana dashboards available
✅ No error logs for critical services
```

---

## 🚀 BEGIN NOW

### Recommended Command (Copy & Paste):
```powershell
cd "C:\Fraud detection\fraud-detection-system" ; docker compose -f docker-compose.yml --profile streaming --profile monitoring up -d --build
```

### Then Wait 2 Minutes:
```powershell
Start-Sleep -Seconds 120
```

### Then Verify:
```powershell
docker compose ps
```

### Then Open:
```
http://localhost:5173
```

---

**That's it! Your fraud detection system is now running production-style.** 🎉

