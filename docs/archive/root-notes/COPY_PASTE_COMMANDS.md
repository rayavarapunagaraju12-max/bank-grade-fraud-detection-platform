# 🚀 COPY & PASTE COMMANDS - YOUR FRAUD DETECTION SYSTEM

## ⚠️ FIRST: NAVIGATE TO PROJECT (MOST IMPORTANT!)

```powershell
cd "C:\Fraud detection\fraud-detection-system"
```

**This is the reason for your error - you MUST be in this directory!**

---

## ✅ VERIFY SYSTEM IS RUNNING

```powershell
docker compose ps
```

**Expected Output:**
```
NAME              SERVICE     STATUS              PORTS
api               api         Up 10 minutes       0.0.0.0:8000->8000/tcp
frontend          frontend    Up 10 minutes       0.0.0.0:5173->5173/tcp
postgres          postgres    Up 10 minutes       0.0.0.0:5432->5432/tcp
redis             redis       Up 10 minutes       0.0.0.0:6379->6379/tcp
```

---

## 🌐 OPEN YOUR DASHBOARDS

### Frontend (Your Main Dashboard)
```
http://localhost:5173
```

### API Documentation (Test Endpoints)
```
http://localhost:8000/docs
```

### Database Access
```powershell
docker compose exec postgres psql -U fraud -d fraud
```
Then type:
```sql
SELECT * FROM alerts LIMIT 5;
\q  -- to exit
```

---

## 📊 GENERATE TEST FRAUD TRANSACTIONS

### Option 1: Generate 100 Transactions (Quick Test)
```powershell
docker compose exec api python -m streaming.transaction_generator.generator --rate 100 --seconds 1 --fraud-ratio 0.1
```

### Option 2: Generate 1,000 Transactions (Load Test)
```powershell
docker compose exec api python -m streaming.transaction_generator.generator --rate 1000 --seconds 1 --fraud-ratio 0.1
```

### Option 3: Continuous Stream (30 seconds)
```powershell
docker compose exec api python -m streaming.transaction_generator.generator --rate 500 --seconds 30 --fraud-ratio 0.1
```

---

## 📈 CHECK FRAUD ALERTS CREATED

### Count Total Alerts
```powershell
docker compose exec postgres psql -U fraud -d fraud -c "SELECT COUNT(*) as total_alerts FROM alerts;"
```

### View Alert Distribution (by Risk Band)
```powershell
docker compose exec postgres psql -U fraud -d fraud -c "
SELECT 
  risk_band,
  COUNT(*) as count,
  ROUND(AVG(score)::numeric, 4) as avg_score,
  MIN(score) as min_score,
  MAX(score) as max_score
FROM alerts
GROUP BY risk_band
ORDER BY risk_band DESC;
"
```

### View Recent Alerts (Last 10)
```powershell
docker compose exec postgres psql -U fraud -d fraud -c "
SELECT 
  transaction_id, 
  account_id,
  score, 
  risk_band, 
  created_at 
FROM alerts 
ORDER BY created_at DESC 
LIMIT 10;
"
```

### View High-Risk Alerts Only
```powershell
docker compose exec postgres psql -U fraud -d fraud -c "
SELECT 
  transaction_id,
  score,
  risk_band,
  created_at
FROM alerts
WHERE risk_band = 'HIGH' OR risk_band = 'CRITICAL'
ORDER BY score DESC
LIMIT 20;
"
```

---

## 🔍 SYSTEM DIAGNOSTICS

### Check API Health
```powershell
curl -X GET http://localhost:8000/health
```

### Check Redis Status
```powershell
docker compose exec redis redis-cli PING
```

### Check Database Connection
```powershell
docker compose exec postgres psql -U fraud -d fraud -c "SELECT version();"
```

### View System Resource Usage
```powershell
docker stats
```

### View Application Logs
```powershell
docker compose logs -f api
```

### View Database Logs
```powershell
docker compose logs -f postgres
```

### View All Logs
```powershell
docker compose logs -f
```

---

## 🛑 STOP & CLEANUP

### Stop All Services (Keep Data)
```powershell
docker compose down
```

### Stop All Services (Delete Data)
```powershell
docker compose down -v
```

### Remove Everything
```powershell
docker compose down -v
docker system prune -a
```

---

## 🔄 RESTART SYSTEM

### Restart All Services
```powershell
docker compose restart
```

### Restart Specific Service
```powershell
docker compose restart api
```

### Rebuild and Restart
```powershell
docker compose down
docker compose up -d --build
```

---

## 📊 PROJECT STATUS QUERIES

### Check Total Tables Created
```powershell
docker compose exec postgres psql -U fraud -d fraud -c "
SELECT COUNT(*) as total_tables 
FROM information_schema.tables 
WHERE table_schema='public';
"
```

### List All Tables
```powershell
docker compose exec postgres psql -U fraud -d fraud -c "\dt"
```

### Check Audit Log Integrity (Hash Chain)
```powershell
docker compose exec postgres psql -U fraud -d fraud -c "
SELECT COUNT(*) as total_audit_logs FROM audit_logs;
"
```

### View Case Statistics
```powershell
docker compose exec postgres psql -U fraud -d fraud -c "
SELECT 
  status,
  COUNT(*) as count
FROM cases
GROUP BY status;
"
```

---

## 💾 BACKUP & EXPORT DATA

### Backup All Data
```powershell
docker compose exec postgres pg_dump -U fraud fraud > fraud_backup.sql
```

### Export Fraud Alerts to CSV
```powershell
docker compose exec postgres psql -U fraud -d fraud -c "
COPY (SELECT * FROM alerts) 
TO STDOUT 
WITH (FORMAT csv, HEADER true);" > alerts_export.csv
```

### Export Audit Logs to CSV
```powershell
docker compose exec postgres psql -U fraud -d fraud -c "
COPY (SELECT * FROM audit_logs) 
TO STDOUT 
WITH (FORMAT csv, HEADER true);" > audit_logs_export.csv
```

---

## 🚀 FULL STARTUP SCRIPT (Copy & Paste All)

```powershell
# ============================================
# FRAUD DETECTION SYSTEM - COMPLETE STARTUP
# ============================================

Write-Host "🚀 Starting Fraud Detection System..." -ForegroundColor Green

# Step 1: Navigate
Write-Host "`n📁 Navigating to project..." -ForegroundColor Cyan
cd "C:\Fraud detection\fraud-detection-system"

# Step 2: Start services
Write-Host "`n🐳 Starting Docker services..." -ForegroundColor Cyan
docker compose -f docker-compose.yml -f docker-compose.demo.yml up -d --build

# Step 3: Wait
Write-Host "`n⏳ Waiting 30 seconds for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Step 4: Check status
Write-Host "`n✅ Service Status:" -ForegroundColor Green
docker compose ps

# Step 5: Generate data
Write-Host "`n📊 Generating 100 test transactions..." -ForegroundColor Cyan
docker compose exec api python -m streaming.transaction_generator.generator --rate 100 --seconds 1 --fraud-ratio 0.1

# Step 6: Check results
Write-Host "`n📈 Checking fraud alerts..." -ForegroundColor Green
docker compose exec postgres psql -U fraud -d fraud -c "SELECT COUNT(*) as alerts FROM alerts;"

# Step 7: Show URLs
Write-Host "`n🌐 Open These URLs:" -ForegroundColor Green
Write-Host "  Frontend:    http://localhost:5173" -ForegroundColor White
Write-Host "  API Docs:    http://localhost:8000/docs" -ForegroundColor White
Write-Host "  Database:    localhost:5432" -ForegroundColor White

Write-Host "`n✅ System is ready!" -ForegroundColor Green
```

---

## 📋 QUICK REFERENCE TABLE

| What | Command |
|------|---------|
| **Navigate** | `cd "C:\Fraud detection\fraud-detection-system"` |
| **Check Status** | `docker compose ps` |
| **View Logs** | `docker compose logs -f api` |
| **Generate Data (100)** | `docker compose exec api python -m streaming.transaction_generator.generator --rate 100 --seconds 1 --fraud-ratio 0.1` |
| **Count Alerts** | `docker compose exec postgres psql -U fraud -d fraud -c "SELECT COUNT(*) FROM alerts;"` |
| **View Alerts** | `docker compose exec postgres psql -U fraud -d fraud -c "SELECT * FROM alerts LIMIT 10;"` |
| **Stop System** | `docker compose down` |
| **Restart System** | `docker compose restart` |
| **View Database** | `docker compose exec postgres psql -U fraud -d fraud` |
| **Check Redis** | `docker compose exec redis redis-cli PING` |
| **Frontend** | http://localhost:5173 |
| **API Docs** | http://localhost:8000/docs |
| **System Stats** | `docker stats` |

---

## ✨ MOST IMPORTANT RULE

**Before running ANY docker compose command, run this FIRST:**

```powershell
cd "C:\Fraud detection\fraud-detection-system"
```

**This is why you got the error!**

---

## 🎯 RECOMMENDED NEXT STEPS

1. **Run this first:**
   ```powershell
   cd "C:\Fraud detection\fraud-detection-system"
   docker compose ps
   ```

2. **Then open this:**
   ```
   http://localhost:5173
   ```

3. **Then generate data:**
   ```powershell
   docker compose exec api python -m streaming.transaction_generator.generator --rate 100 --seconds 1 --fraud-ratio 0.1
   ```

4. **Then check results:**
   ```powershell
   docker compose exec postgres psql -U fraud -d fraud -c "SELECT COUNT(*) FROM alerts;"
   ```

---

## 📞 IF YOU GET AN ERROR

| Error | Solution |
|-------|----------|
| "no configuration file" | Run: `cd "C:\Fraud detection\fraud-detection-system"` first |
| "Connection refused" | Wait 30 seconds for services to start |
| "Port already in use" | Run: `docker compose down` first |
| "Database error" | Check logs: `docker compose logs postgres` |
| "API not responding" | Check: `docker compose logs api` |

---

## 🎉 YOU'RE ALL SET!

Your fraud detection system is running. Copy any command above and it will work!

**Start with:**
```powershell
cd "C:\Fraud detection\fraud-detection-system"
docker compose ps
```

**Then open:**
```
http://localhost:5173
```

**Enjoy your production-style fraud detection system!** 🚀

