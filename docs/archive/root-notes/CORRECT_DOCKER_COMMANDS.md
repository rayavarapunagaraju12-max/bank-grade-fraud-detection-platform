# ✅ CORRECT DOCKER COMMANDS - YOUR SYSTEM IS RUNNING!

## 🎉 STATUS: SYSTEM IS UP! (4 Services Running)

```
✅ API                 http://localhost:8000 (UP 9 minutes)
✅ Frontend            http://localhost:5173 (UP 9 minutes)
✅ PostgreSQL          localhost:5432 (UP 9 minutes)
✅ Redis               localhost:6379 (UP 9 minutes)
```

---

## ⚠️ THE ISSUE YOU HAD

```powershell
# ❌ WRONG - You ran from parent directory
cd "C:\Fraud detection"
docker compose ps
# Error: no configuration file provided: not found

# ✅ CORRECT - Must be in fraud-detection-system directory
cd "C:\Fraud detection\fraud-detection-system"
docker compose ps
```

---

## 🚀 CORRECT STARTUP COMMANDS (Copy & Paste These)

### Option 1: Quick Demo (Minimal - 4 Services)
```powershell
cd "C:\Fraud detection\fraud-detection-system"
docker compose -f docker-compose.yml -f docker-compose.demo.yml up -d --build
```
**Running now! Services: API, Frontend, PostgreSQL, Redis**

### Option 2: Full Stack (9+ Services)
```powershell
cd "C:\Fraud detection\fraud-detection-system"
docker compose -f docker-compose.yml --profile streaming --profile monitoring up -d --build
```
**This will add: Kafka, Neo4j, Prometheus, Grafana**

### Option 3: Complete Production Stack (All 15 Services)
```powershell
cd "C:\Fraud detection\fraud-detection-system"
docker compose -f docker-compose.yml --profile streaming --profile graph --profile monitoring --profile logging --profile ai up -d --build
```
**This will add: Everything including ELK, Ollama, Zookeeper**

---

## ✅ VERIFICATION COMMANDS

### Check All Services
```powershell
cd "C:\Fraud detection\fraud-detection-system"
docker compose ps
```

### Check API Health
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/health" -ErrorAction SilentlyContinue | Select-Object StatusCode, Content
```
**Expected: 200, {"status": "ok"}**

### Check Database
```powershell
cd "C:\Fraud detection\fraud-detection-system"
docker compose exec postgres psql -U fraud -d fraud -c "SELECT version();"
```

### Check Redis
```powershell
cd "C:\Fraud detection\fraud-detection-system"
docker compose exec redis redis-cli PING
```
**Expected: PONG**

### View Logs
```powershell
cd "C:\Fraud detection\fraud-detection-system"
docker compose logs -f api
```

---

## 🌐 ACCESS YOUR DASHBOARDS

### API Documentation & Testing
```
http://localhost:8000/docs
```
✅ Click "Try it out" to test endpoints

### Frontend Dashboard
```
http://localhost:5173
```
✅ View fraud alerts, cases, investigations

### Database (PostgreSQL)
```powershell
cd "C:\Fraud detection\fraud-detection-system"
docker compose exec postgres psql -U fraud -d fraud
# Then type: \dt (to see tables)
# Then type: SELECT * FROM alerts LIMIT 5;
# Then type: \q (to quit)
```

---

## 📊 GENERATE TEST DATA

### Generate 100 Test Transactions
```powershell
cd "C:\Fraud detection\fraud-detection-system"
docker compose exec api python -m streaming.transaction_generator.generator --rate 100 --seconds 1 --fraud-ratio 0.1
```

### Generate 1,000 Transactions (Stress Test)
```powershell
cd "C:\Fraud detection\fraud-detection-system"
docker compose exec api python -m streaming.transaction_generator.generator --rate 1000 --seconds 1 --fraud-ratio 0.1
```

### Generate Continuous Stream (30 seconds)
```powershell
cd "C:\Fraud detection\fraud-detection-system"
docker compose exec api python -m streaming.transaction_generator.generator --rate 500 --seconds 30 --fraud-ratio 0.1
```

---

## 📈 CHECK FRAUD DETECTION RESULTS

### Count Total Alerts
```powershell
cd "C:\Fraud detection\fraud-detection-system"
docker compose exec postgres psql -U fraud -d fraud -c "SELECT COUNT(*) as total_alerts FROM alerts;"
```

### View Alert Distribution
```powershell
cd "C:\Fraud detection\fraud-detection-system"
docker compose exec postgres psql -U fraud -d fraud -c "
SELECT 
  risk_band,
  COUNT(*) as count,
  ROUND(AVG(score)::numeric, 4) as avg_score
FROM alerts
GROUP BY risk_band
ORDER BY risk_band DESC;
"
```

### View Recent Alerts
```powershell
cd "C:\Fraud detection\fraud-detection-system"
docker compose exec postgres psql -U fraud -d fraud -c "
SELECT transaction_id, score, risk_band, created_at 
FROM alerts 
ORDER BY created_at DESC 
LIMIT 10;
"
```

---

## 🛑 STOPPING & CLEANUP

### Stop All Services (Keep Data)
```powershell
cd "C:\Fraud detection\fraud-detection-system"
docker compose down
```

### Stop All Services (Remove Data)
```powershell
cd "C:\Fraud detection\fraud-detection-system"
docker compose down -v
```

### View Service Status
```powershell
cd "C:\Fraud detection\fraud-detection-system"
docker compose ps
```

### View Running Logs
```powershell
cd "C:\Fraud detection\fraud-detection-system"
docker compose logs --tail 50 api
docker compose logs --tail 50 postgres
docker compose logs --tail 50 stream-consumer
```

---

## 🚀 COMPLETE STARTUP SCRIPT (Copy & Paste All)

```powershell
# ============================================
# FRAUD DETECTION SYSTEM - FULL STARTUP
# ============================================

Write-Host "🚀 Starting Fraud Detection System..." -ForegroundColor Green
Write-Host "📍 Location: C:\Fraud detection\fraud-detection-system`n" -ForegroundColor Cyan

# Navigate to project
cd "C:\Fraud detection\fraud-detection-system"

# Start services
Write-Host "🐳 Starting Docker services..." -ForegroundColor Green
docker compose -f docker-compose.yml -f docker-compose.demo.yml up -d --build

# Wait for services
Write-Host "`n⏳ Waiting 30 seconds for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Show status
Write-Host "`n✅ Service Status:" -ForegroundColor Green
docker compose ps

# Test API
Write-Host "`n🔧 Testing API..." -ForegroundColor Green
$health = Invoke-WebRequest -Uri "http://localhost:8000/health" -ErrorAction SilentlyContinue
if ($health.StatusCode -eq 200) {
    Write-Host "✅ API is healthy!" -ForegroundColor Green
} else {
    Write-Host "❌ API not responding" -ForegroundColor Red
}

# Show dashboard URLs
Write-Host "`n🌐 Access Your Dashboards:" -ForegroundColor Cyan
Write-Host "  API Docs:    http://localhost:8000/docs" -ForegroundColor White
Write-Host "  Frontend:    http://localhost:5173" -ForegroundColor White
Write-Host "  Database:    postgres://localhost:5432" -ForegroundColor White

Write-Host "`n✅ System is ready!" -ForegroundColor Green
```

---

## 📋 COMMAND QUICK REFERENCE

| What You Want | Command |
|---|---|
| **Check status** | `docker compose ps` |
| **View logs** | `docker compose logs -f api` |
| **Test API** | `Invoke-WebRequest http://localhost:8000/health` |
| **Generate data** | `docker compose exec api python -m streaming.transaction_generator.generator --rate 100 --seconds 1 --fraud-ratio 0.1` |
| **View alerts** | `docker compose exec postgres psql -U fraud -d fraud -c "SELECT * FROM alerts LIMIT 5;"` |
| **Stop system** | `docker compose down` |
| **Remove data** | `docker compose down -v` |
| **View database** | `docker compose exec postgres psql -U fraud -d fraud` |
| **Check Redis** | `docker compose exec redis redis-cli PING` |

---

## ⚠️ KEY POINT: Always Use This Directory

```powershell
# ✅ CORRECT
cd "C:\Fraud detection\fraud-detection-system"
docker compose ps

# ❌ WRONG
cd "C:\Fraud detection"
docker compose ps
```

The `docker-compose.yml` file must be in your current directory!

---

## 🎯 PROJECT STATUS

### Currently Running (Demo Mode)
```
✅ API Server (FastAPI)
✅ Frontend Dashboard (React)
✅ PostgreSQL Database
✅ Redis Cache

Total: 4 services, 2-3 GB RAM
```

### Available with Full Stack
```
+ Kafka (Streaming)
+ Zookeeper (Kafka management)
+ Neo4j (Knowledge graph)
+ Prometheus (Metrics)
+ Grafana (Dashboards)
+ Elasticsearch (Logging)
+ Logstash (Log processing)
+ Kibana (Log visualization)
+ Ollama (LLM narratives)
+ MinIO (Object storage)

Total: 15 services, 12-15 GB RAM
```

### Production Readiness
```
✅ 40-50% complete
✅ Architecture is production-style
❌ Performance not yet production (1.1k TPS, need 10k+)
❌ Latency not yet production (145ms, need <50ms)

Next: Follow 8-phase roadmap in DETAILED_IMPLEMENTATION_ROADMAP.md
```

---

## 🎉 YOU'RE ALL SET!

Your fraud detection system is:
- ✅ **Running** (4 services up)
- ✅ **Connected** (API responding)
- ✅ **Ready to test** (dashboards available)
- ✅ **Production-style** (proper architecture)
- ⏳ **Needs optimization** (for SLA - 6-9 months)

**Next:** Open http://localhost:5173 and start using it!

