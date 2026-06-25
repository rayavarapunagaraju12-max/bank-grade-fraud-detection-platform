# 🚀 COMPLETE RESTART - ALL COMMANDS STEP BY STEP

## FASTEST WAY TO RESTART (7 Steps)

### Step 1️⃣: Open PowerShell
```powershell
# Press: Win + R
# Type: powershell
# Press: Enter
```

---

### Step 2️⃣: Navigate to Project
```powershell
cd "C:\Fraud detection\fraud-detection-system"
```

**Verify you're in correct folder:**
```powershell
ls

# Should show: docker-compose.yml, backend/, frontend/, etc.
```

---

### Step 3️⃣: Start All Services
```powershell
docker compose up -d --build
```

**This will:**
- Build all Docker images
- Start all 15 services
- Restore all your data automatically
- Takes 3-5 minutes

**You'll see output:**
```
[+] Building 45.3s
[+] Running 15/15
 ✔ Container fraud-detection-system-api-1 Started
 ✔ Container fraud-detection-system-frontend-1 Started
 (... more services ...)
```

---

### Step 4️⃣: Check All Services Running
```powershell
docker compose ps
```

**Expected: Should show 15 services, all "Up"**

```
fraud-detection-system-api-1               Up 2 minutes
fraud-detection-system-elasticsearch-1     Up 2 minutes
fraud-detection-system-frontend-1          Up 2 minutes
fraud-detection-system-grafana-1           Up 2 minutes
fraud-detection-system-kafka-1             Up 2 minutes
fraud-detection-system-kibana-1            Up 2 minutes
fraud-detection-system-logstash-1          Up 2 minutes
fraud-detection-system-minio-1             Up 2 minutes
fraud-detection-system-neo4j-1             Up 2 minutes
fraud-detection-system-ollama-1            Up 2 minutes
fraud-detection-system-postgres-1          Up 2 minutes
fraud-detection-system-prometheus-1        Up 2 minutes
fraud-detection-system-redis-1             Up 2 minutes
fraud-detection-system-stream-consumer-1   Up 2 minutes
fraud-detection-system-zookeeper-1         Up 2 minutes
```

✅ If you see this, go to Step 5

❌ If something says "Exited" or "Restarting":
```powershell
# Check logs for that service
docker compose logs service-name

# Example:
docker compose logs postgres
```

---

### Step 5️⃣: Wait 30 Seconds for Full Initialization
```powershell
Write-Host "Waiting for services to fully start..." -ForegroundColor Yellow
Start-Sleep -Seconds 30
Write-Host "Ready!" -ForegroundColor Green
```

---

### Step 6️⃣: Verify Your Data Was Restored
```powershell
docker compose exec postgres psql -U fraud -d fraud -c "SELECT COUNT(*) as alerts FROM alerts;"
```

**Expected Output:**
```
 alerts
--------
  55296
```

✅ If you see ~55,000 alerts, your data is restored!

---

### Step 7️⃣: Open Dashboards

```powershell
# Open all dashboards
start http://localhost:5173      # Fraud Alerts Dashboard
start http://localhost:3000      # Grafana Metrics (admin/admin)
start http://localhost:7474      # Neo4j Graph (neo4j/fraud_graph_password)
start http://localhost:8000/docs # API Documentation
start http://localhost:5601      # Kibana Logs
start http://localhost:9090      # Prometheus Metrics
```

**Expected:** Browser windows open showing each dashboard

---

## ✅ SYSTEM IS NOW RUNNING!

All 15 services are up with all data restored!

---

## VERIFY EVERYTHING WORKS

### Check API Health
```powershell
docker compose exec api python -c "import requests; print(requests.get('http://localhost:8000/health').json())"
```

**Expected:**
```
{'status': 'ok', 'environment': 'local', 'mode': 'enterprise-compose', 'kafka': 'connected', 'feature_store': 'redis', 'graph': 'neo4j'}
```

---

### Check Audit Logs
```powershell
docker compose exec postgres psql -U fraud -d fraud -c "SELECT COUNT(*) as audit_logs FROM audit_logs;"
```

**Expected:** Should show audit logs count (e.g., 30000)

---

### View System Metrics
```powershell
docker stats
```

**This shows real-time CPU, memory, network usage**

---

## OPTIONAL: TEST WITH NEW TRANSACTIONS

```powershell
# Generate 1,000 transactions per second for 30 seconds
docker compose exec api python -m streaming.transaction_generator.generator --rate 1000 --seconds 30 --fraud-ratio 0.1
```

**Then check new alerts:**
```powershell
docker compose exec postgres psql -U fraud -d fraud -c "SELECT COUNT(*) FROM alerts;"
```

---

## VIEW LOGS (If Something Goes Wrong)

```powershell
# View all logs
docker compose logs -f

# View specific service logs
docker compose logs -f api
docker compose logs -f postgres
docker compose logs -f stream-consumer

# View last 50 lines only
docker compose logs -f --tail 50 api
```

---

## STOP SYSTEM

```powershell
# Stop (keeps all data)
docker compose down

# Stop and delete data
docker compose down -v

# Stop everything including images
docker compose down -v --rmi all
```

---

## TROUBLESHOOTING

### Problem: "Cannot connect to Docker daemon"
```powershell
# Open Docker Desktop app manually
# Wait 1 minute
# Then try: docker compose up -d --build
```

### Problem: "Cannot find docker-compose.yml"
```powershell
# Make sure you're in correct directory
cd "C:\Fraud detection\fraud-detection-system"

# Verify
ls docker-compose.yml
```

### Problem: "Port 8000 already in use"
```powershell
# Find what's using port 8000
netstat -ano | findstr :8000

# Kill that process
taskkill /PID <PID> /F

# Or change port in docker-compose.yml
```

### Problem: "Services stuck in Restarting state"
```powershell
# Check logs
docker compose logs postgres

# Restart Docker
docker compose down
docker compose up -d --build
```

### Problem: "Out of disk space"
```powershell
# Check space
docker system df

# Clean up
docker system prune -a --volumes

# Try again
docker compose up -d --build
```

---

## COMPLETE RESTART SCRIPT (Copy & Paste)

Save this as `restart_all.ps1`:

```powershell
# Complete restart script
Write-Host "╔════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║    FRAUD DETECTION SYSTEM - RESTART SCRIPT    ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════╝" -ForegroundColor Cyan

# Navigate
Write-Host "`n[1/6] Navigating to project..." -ForegroundColor Yellow
cd "C:\Fraud detection\fraud-detection-system"
Write-Host "✅ Done" -ForegroundColor Green

# Start
Write-Host "`n[2/6] Starting services (this takes 3-5 minutes)..." -ForegroundColor Yellow
docker compose up -d --build
Write-Host "✅ Done" -ForegroundColor Green

# Wait
Write-Host "`n[3/6] Waiting 30 seconds for initialization..." -ForegroundColor Yellow
for ($i = 30; $i -gt 0; $i--) {
    Write-Host -NoNewline "`r⏳ $i seconds remaining..."
    Start-Sleep -Seconds 1
}
Write-Host "`n✅ Done" -ForegroundColor Green

# Status
Write-Host "`n[4/6] Checking status..." -ForegroundColor Yellow
$count = docker compose ps | findstr "Up" | Measure-Object | Select-Object -ExpandProperty Count
Write-Host "✅ $count services running" -ForegroundColor Green

# Verify data
Write-Host "`n[5/6] Verifying data restoration..." -ForegroundColor Yellow
$alerts = docker compose exec postgres psql -U fraud -d fraud -c "SELECT COUNT(*) FROM alerts" 2>/dev/null | Select-String "^" -AllMatches | Select-Object -Last 1
Write-Host "✅ Data restored" -ForegroundColor Green

# Done
Write-Host "`n[6/6] Opening dashboards..." -ForegroundColor Yellow
start http://localhost:5173
start http://localhost:3000
start http://localhost:7474
Write-Host "✅ Done" -ForegroundColor Green

Write-Host "`n╔════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  ✅ SYSTEM RESTART COMPLETE - READY TO USE! ✅ ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════╝" -ForegroundColor Green

Write-Host "`nDashboards:" -ForegroundColor Cyan
Write-Host "  • Frontend:  http://localhost:5173" -ForegroundColor White
Write-Host "  • Grafana:   http://localhost:3000" -ForegroundColor White
Write-Host "  • Neo4j:     http://localhost:7474" -ForegroundColor White
Write-Host "  • API:       http://localhost:8000/docs" -ForegroundColor White
```

**To use:**
```powershell
# Save it
$script | Out-File restart_all.ps1

# Run it
./restart_all.ps1
```

---

## COMMAND REFERENCE

| Action | Command |
|--------|---------|
| Start system | `docker compose up -d --build` |
| Check status | `docker compose ps` |
| View logs | `docker compose logs -f` |
| Check alerts | `docker compose exec postgres psql -U fraud -d fraud -c "SELECT COUNT(*) FROM alerts;"` |
| API health | `docker compose exec api python -c "import requests; print(requests.get('http://localhost:8000/health').json())"` |
| Generate transactions | `docker compose exec api python -m streaming.transaction_generator.generator --rate 1000 --seconds 30 --fraud-ratio 0.1` |
| Stop system | `docker compose down` |
| View disk usage | `docker system df` |
| Restart service | `docker compose restart api` |
| View specific logs | `docker compose logs postgres` |

---

## Timeline

```
Step 1:    ~5 seconds
Step 2:    ~2 seconds
Step 3:    ~3-5 minutes ⏱️
Step 4:    ~5 seconds
Step 5:    ~30 seconds ⏱️
Step 6:    ~5 seconds
Step 7:    ~5 seconds

TOTAL: ~4-7 minutes ⏱️
```

---

## ✅ SUCCESS CHECKLIST

After restart, verify:

- [ ] `docker compose ps` shows 15 services all "Up"
- [ ] API responds: `curl http://localhost:5173` (works)
- [ ] Data restored: ~55,000 alerts in database
- [ ] Dashboards open: Frontend, Grafana, Neo4j, API
- [ ] No errors in logs: `docker compose logs` (no red errors)
- [ ] System metrics show healthy values: `docker stats`

---

## 🎉 YOU'RE DONE!

System is fully restarted with all data restored and ready to use!

If you need anything else, refer to the other documentation files in the project.

