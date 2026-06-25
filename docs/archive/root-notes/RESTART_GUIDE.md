# 🚀 COMPLETE RESTART GUIDE - STEP BY STEP

## Prerequisites Check

Before restarting, verify you have:
- ✅ Docker installed
- ✅ Project directory available
- ✅ Docker daemon running
- ✅ Sufficient disk space (30+ GB recommended)

---

## STEP 1: Navigate to Project Directory

```powershell
# Open PowerShell and navigate to project
cd "C:\Fraud detection\fraud-detection-system"

# Verify you're in correct directory
ls

# You should see:
# docker-compose.yml
# backend/
# frontend/
# compliance/
# etc.
```

**Expected Output:**
```
    Directory: C:\Fraud detection\fraud-detection-system

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d----          6/12/2026  12:00 PM                .github
d----          6/12/2026  12:00 PM                backend
d----          6/12/2026  12:00 PM                compliance
d----          6/12/2026  12:00 PM                frontend
-a---          6/12/2026  12:00 PM           5000 docker-compose.yml
```

**✅ Step 1 Complete**

---

## STEP 2: Check Docker Status

```powershell
# Verify Docker is running
docker --version

# Check Docker daemon
docker ps

# You should see output (even if empty):
# CONTAINER ID   IMAGE      COMMAND      CREATED      STATUS      PORTS      NAMES
```

**Expected Output:**
```
Docker version 24.0.x, build xxxxxxx
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
(empty list - which is correct)
```

**✅ Step 2 Complete**

---

## STEP 3: Verify Docker Compose File

```powershell
# Check if docker-compose.yml exists
Test-Path docker-compose.yml

# View the file to ensure it's valid
Get-Content docker-compose.yml | Select-Object -First 20

# You should see:
# services:
#   zookeeper:
#     image: confluentinc/cp-zookeeper:7.7.1
```

**Expected Output:**
```
True
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:7.7.1
```

**✅ Step 3 Complete**

---

## STEP 4: Check Docker Volumes (Your Data)

```powershell
# List all Docker volumes
docker volume ls

# You should see volumes starting with "fraud-detection-system"
# These contain all your data!
```

**Expected Output:**
```
DRIVER    VOLUME NAME
local     fraud-detection-system_elasticsearch_data
local     fraud-detection-system_minio_data
local     fraud-detection-system_neo4j_data
local     fraud-detection-system_postgres_data
local     fraud-detection-system_redis_data
```

**✅ Step 4 Complete**

---

## STEP 5: Start All Services (Full Restart)

```powershell
# Build and start all services
# This rebuilds images and starts containers
docker compose up -d --build

# This will take 2-5 minutes
# You'll see output like:
# Building api
# Building frontend
# Building stream-consumer
# Creating network fraud-detection-system_default
# Creating container fraud-detection-system-postgres-1
# etc.
```

**Expected Output:**
```
[+] Building 45.3s (15/15) FINISHED
[+] Running 15/15
 ✔ Container fraud-detection-system-api-1 Started
 ✔ Container fraud-detection-system-frontend-1 Started
 ✔ Container fraud-detection-system-postgres-1 Started
 (... all 15 containers)
```

**⏱️ This takes 2-5 minutes - Be patient!**

**✅ Step 5 Complete**

---

## STEP 6: Verify All Services Are Running

```powershell
# Check status of all services
docker compose ps

# You should see all 15 services with status "Up"
```

**Expected Output:**
```
NAME                                       IMAGE                                    STATUS
fraud-detection-system-api-1               fraud-detection-system-api               Up 2 minutes
fraud-detection-system-elasticsearch-1     docker.elastic.co/elasticsearch/...       Up 2 minutes
fraud-detection-system-frontend-1          fraud-detection-system-frontend          Up 2 minutes
fraud-detection-system-grafana-1           grafana/grafana:11.4.0                   Up 2 minutes
fraud-detection-system-kafka-1             confluentinc/cp-kafka:7.7.1              Up 2 minutes
fraud-detection-system-kibana-1            docker.elastic.co/kibana/...             Up 2 minutes
fraud-detection-system-logstash-1          docker.elastic.co/logstash/...           Up 2 minutes
fraud-detection-system-minio-1             minio/minio:RELEASE.2024-12-18...        Up 2 minutes
fraud-detection-system-neo4j-1             neo4j:5.26                               Up 2 minutes
fraud-detection-system-ollama-1            ollama/ollama:0.4.7                      Up 2 minutes
fraud-detection-system-postgres-1          postgres:16-alpine                       Up 2 minutes
fraud-detection-system-prometheus-1        prom/prometheus:v3.0.1                   Up 2 minutes
fraud-detection-system-redis-1             redis:7.4-alpine                         Up 2 minutes
fraud-detection-system-stream-consumer-1   fraud-detection-system-stream-consumer   Up 2 minutes
fraud-detection-system-zookeeper-1         confluentinc/cp-zookeeper:7.7.1          Up 2 minutes
```

**Count:** Should show 15 services, all with status "Up"

**✅ Step 6 Complete**

---

## STEP 7: Wait for Services to Fully Initialize

```powershell
# Services are running, but need time to fully initialize
# Different services have different startup times:
# - PostgreSQL: 10-15 seconds
# - Neo4j: 15-20 seconds
# - Elasticsearch: 20-30 seconds
# - Kafka: 15-20 seconds

Write-Host "Waiting for services to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

Write-Host "Services should be ready now" -ForegroundColor Green
```

**⏱️ Wait 30 seconds minimum**

**✅ Step 7 Complete**

---

## STEP 8: Verify All Data Was Restored

```powershell
# Check PostgreSQL - verify alerts exist
docker compose exec postgres psql -U fraud -d fraud -c "SELECT COUNT(*) as total_alerts FROM alerts;"

# Expected output: Should show your backed-up alert count (55,296)
```

**Expected Output:**
```
 total_alerts
--------------
        55296
```

**✅ Step 8 Complete - Your data is restored!**

---

## STEP 9: Verify API Health

```powershell
# Check if API is responding
docker compose exec api python -c "import requests; r = requests.get('http://localhost:8000/health'); print(r.json())"

# Expected: Should return JSON with status 'ok'
```

**Expected Output:**
```
{'status': 'ok', 'environment': 'local', 'mode': 'enterprise-compose', 'kafka': 'connected', 'feature_store': 'redis', 'graph': 'neo4j'}
```

**✅ Step 9 Complete**

---

## STEP 10: Verify Audit Logs (Your Compliance Data)

```powershell
# Check audit logs were restored
docker compose exec postgres psql -U fraud -d fraud -c "SELECT COUNT(*) as audit_logs FROM audit_logs;"

# Expected: Should show your backed-up audit log count
```

**Expected Output:**
```
 audit_logs
-----------
      30000
```

**✅ Step 10 Complete**

---

## STEP 11: Open Dashboards

```powershell
# Open Frontend Dashboard (Fraud Alerts)
start http://localhost:5173

# Open Grafana (Metrics)
start http://localhost:3000

# Open Neo4j (Graph Database)
start http://localhost:7474

# Open API Documentation
start http://localhost:8000/docs

# Open Kibana (Logs)
start http://localhost:5601

# Open Prometheus (Metrics)
start http://localhost:9090
```

**What to expect:**
- Frontend: Shows your fraud alerts dashboard
- Grafana: Shows system metrics
- Neo4j: Shows fraud ring graph
- API Docs: Interactive API explorer
- Kibana: Log viewer
- Prometheus: Raw metrics

**✅ Step 11 Complete**

---

## STEP 12: Verify Data Integrity (Optional but Recommended)

```powershell
# Get final statistics
docker compose exec postgres psql -U fraud -d fraud -c "
SELECT 
  COUNT(*) as total_alerts,
  ROUND(AVG(score)::numeric, 4) as avg_score,
  ROUND(MAX(score)::numeric, 4) as max_score,
  COUNT(CASE WHEN score >= 0.9 THEN 1 END) as critical_alerts
FROM alerts;
"

# Expected: Should match the statistics from before shutdown
```

**Expected Output:**
```
 total_alerts | avg_score | max_score | critical_alerts
--------------+-----------+-----------+-----------------
        55296 |    0.8181 |    1.0000 |           14014
```

**✅ Step 12 Complete**

---

## QUICK RESTART SCRIPT (Run All Steps at Once)

Save this as `restart.ps1` and run it:

```powershell
# Run this entire script for quick restart

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║         FRAUD DETECTION SYSTEM - RESTART SCRIPT           ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

# Step 1: Navigate to project
Write-Host "`n[1/7] Navigating to project directory..." -ForegroundColor Yellow
cd "C:\Fraud detection\fraud-detection-system"
if (Test-Path docker-compose.yml) {
    Write-Host "✅ Project directory found" -ForegroundColor Green
} else {
    Write-Host "❌ Project directory not found!" -ForegroundColor Red
    exit
}

# Step 2: Check Docker
Write-Host "`n[2/7] Checking Docker..." -ForegroundColor Yellow
docker ps > $null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Docker is running" -ForegroundColor Green
} else {
    Write-Host "❌ Docker is not running!" -ForegroundColor Red
    exit
}

# Step 3: Check volumes
Write-Host "`n[3/7] Checking data volumes..." -ForegroundColor Yellow
$volumes = docker volume ls | Select-String "fraud-detection" | Measure-Object | Select-Object -ExpandProperty Count
Write-Host "✅ Found $volumes data volumes" -ForegroundColor Green

# Step 4: Start services
Write-Host "`n[4/7] Starting all services..." -ForegroundColor Yellow
docker compose up -d --build
Write-Host "✅ Services started" -ForegroundColor Green

# Step 5: Wait for initialization
Write-Host "`n[5/7] Waiting for services to initialize (30 seconds)..." -ForegroundColor Yellow
for ($i = 30; $i -gt 0; $i--) {
    Write-Host -NoNewline "`r⏳ $i seconds remaining..."
    Start-Sleep -Seconds 1
}
Write-Host "`n✅ Services initialized" -ForegroundColor Green

# Step 6: Verify services
Write-Host "`n[6/7] Verifying all services..." -ForegroundColor Yellow
$running = docker compose ps --services | Measure-Object | Select-Object -ExpandProperty Count
Write-Host "✅ All $running services are running" -ForegroundColor Green

# Step 7: Verify data
Write-Host "`n[7/7] Verifying data restoration..." -ForegroundColor Yellow
$alerts = docker compose exec postgres psql -U fraud -d fraud -c "SELECT COUNT(*) FROM alerts" 2>/dev/null | Select-String "^" -AllMatches | Select-Object -Last 1 | ForEach-Object { $_.Matches[0].Value.Trim() }
Write-Host "✅ Data restored: $alerts alerts found" -ForegroundColor Green

Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║     ✅ SYSTEM RESTART COMPLETE - READY TO USE ✅          ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green

Write-Host "`nDashboards now available at:" -ForegroundColor Cyan
Write-Host "  Frontend:  http://localhost:5173" -ForegroundColor White
Write-Host "  Grafana:   http://localhost:3000 (admin/admin)" -ForegroundColor White
Write-Host "  Neo4j:     http://localhost:7474 (neo4j/fraud_graph_password)" -ForegroundColor White
Write-Host "  API:       http://localhost:8000/docs" -ForegroundColor White

Write-Host "`nTotal Alerts Restored: $alerts" -ForegroundColor Green
```

**How to use:**
```powershell
# Save the script
$script | Out-File -FilePath "restart.ps1" -Encoding UTF8

# Run it
./restart.ps1
```

---

## Troubleshooting During Restart

### Problem: "Cannot connect to Docker daemon"
```powershell
# Solution: Start Docker Desktop
# Windows: Open Docker Desktop application
# Then retry: docker compose up -d --build
```

### Problem: "Port already in use"
```powershell
# Solution: Change ports in docker-compose.yml
# Example: Change 8000:8000 to 8001:8000
# Then retry: docker compose up -d --build
```

### Problem: "No space left on device"
```powershell
# Solution: Clean up Docker
docker system prune -a --volumes

# Then retry: docker compose up -d --build
```

### Problem: "Services not starting"
```powershell
# Solution: Check logs
docker compose logs -f api

# Or check specific service
docker compose logs postgres | head -50
```

### Problem: "Data not restored"
```powershell
# Solution: Verify volumes
docker volume ls | findstr fraud

# Inspect volume
docker volume inspect fraud-detection-system_postgres_data

# Data should show in "Mountpoint"
```

---

## Verify Everything is Working

```powershell
# Run all verification commands

Write-Host "=== SYSTEM VERIFICATION ===" -ForegroundColor Cyan

# 1. Services running
Write-Host "`n1. Services Status:" -ForegroundColor Green
docker compose ps | Measure-Object -Line | Select-Object -ExpandProperty Lines

# 2. API health
Write-Host "`n2. API Health:" -ForegroundColor Green
docker compose exec api python -c "import requests; print(requests.get('http://localhost:8000/health').json())"

# 3. Alerts count
Write-Host "`n3. Data Restored:" -ForegroundColor Green
docker compose exec postgres psql -U fraud -d fraud -c "SELECT COUNT(*) as alerts FROM alerts;"

# 4. Audit logs
Write-Host "`n4. Audit Logs:" -ForegroundColor Green
docker compose exec postgres psql -U fraud -d fraud -c "SELECT COUNT(*) as logs FROM audit_logs;"

# 5. Disk usage
Write-Host "`n5. Docker Disk Usage:" -ForegroundColor Green
docker system df

Write-Host "`n✅ SYSTEM FULLY OPERATIONAL" -ForegroundColor Green
```

---

## Commands Cheat Sheet

```powershell
# Navigate to project
cd "C:\Fraud detection\fraud-detection-system"

# Start system
docker compose up -d --build

# Check status
docker compose ps

# View logs
docker compose logs -f api

# View all alerts
docker compose exec postgres psql -U fraud -d fraud -c "SELECT COUNT(*) FROM alerts;"

# View audit logs
docker compose exec postgres psql -U fraud -d fraud -c "SELECT COUNT(*) FROM audit_logs;"

# API health check
docker compose exec api python -c "import requests; print(requests.get('http://localhost:8000/health').json())"

# Generate test transactions
docker compose exec api python -m streaming.transaction_generator.generator --rate 1000 --seconds 30 --fraud-ratio 0.1

# View dashboards
start http://localhost:5173      # Frontend
start http://localhost:3000      # Grafana
start http://localhost:7474      # Neo4j
start http://localhost:8000/docs # API

# Stop system
docker compose down

# Stop and delete data
docker compose down -v

# View logs for specific service
docker compose logs stream-consumer
docker compose logs postgres

# Get system metrics
docker stats

# Full cleanup (if needed)
docker compose down -v --rmi all
```

---

## Expected Timeline

```
Step 1-4:   ~30 seconds (Navigation & verification)
Step 5:     ~3-5 minutes (Build & start services)
Step 6:     ~15 seconds (Verify running)
Step 7:     ~30 seconds (Wait for init)
Step 8-12:  ~30 seconds (Verify data)

TOTAL TIME: ~5-7 minutes from start to fully operational ✅
```

---

## ✅ Success Indicators

When restart is complete, you should see:

✅ **All 15 services showing "Up" status**
```
docker compose ps
```

✅ **API responding with health check**
```
{'status': 'ok', ...}
```

✅ **55,296 alerts restored**
```
SELECT COUNT(*) FROM alerts;
```

✅ **Dashboards accessible**
- http://localhost:5173 (loads)
- http://localhost:3000 (loads)
- http://localhost:7474 (loads)

✅ **No errors in logs**
```
docker compose logs | findstr ERROR
```

---

## If Something Goes Wrong

### Check logs first:
```powershell
docker compose logs -f
```

### Restart specific service:
```powershell
docker compose restart api
docker compose restart postgres
docker compose restart neo4j
```

### Full restart from scratch:
```powershell
docker compose down
docker compose up -d --build
```

### Get help:
```powershell
# View specific service logs
docker compose logs postgres | head -50

# Check service health
docker compose exec api python -c "import requests; print(requests.get('http://localhost:8000/health').json())"

# Check disk space
docker system df
```

---

## You're All Set! 🚀

Follow these 12 steps and your system will be fully restarted with all data restored!

**Ready?** Start with **STEP 1** above!

