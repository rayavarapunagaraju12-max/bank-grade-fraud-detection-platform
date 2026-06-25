# QUICK START - RUN THESE COMMANDS ONE BY ONE

## Copy & Paste These Commands in PowerShell

### Command 1: Navigate to Project
```powershell
cd "C:\Fraud detection\fraud-detection-system"
```

### Command 2: Start All Services (Build + Run)
```powershell
docker compose up -d --build
```
**⏱️ Wait 3-5 minutes for this to complete**

### Command 3: Check Status
```powershell
docker compose ps
```
**Expected: All 15 services showing "Up"**

### Command 4: Wait for Initialization
```powershell
Start-Sleep -Seconds 30
```
**Wait 30 seconds**

### Command 5: Verify Data Restored
```powershell
docker compose exec postgres psql -U fraud -d fraud -c "SELECT COUNT(*) as alerts FROM alerts;"
```
**Expected: Should show 55,296 alerts**

### Command 6: Verify API Health
```powershell
docker compose exec api python -c "import requests; print(requests.get('http://localhost:8000/health').json())"
```
**Expected: Should return {'status': 'ok', ...}**

### Command 7: Open Dashboards
```powershell
start http://localhost:5173
start http://localhost:3000
start http://localhost:7474
start http://localhost:8000/docs
```

---

## That's It! System is Running ✅

All 15 services are up with all your data restored!

---

## OPTIONAL: Generate Test Transactions

```powershell
# Generate 5,000 transactions over 30 seconds
docker compose exec api python -m streaming.transaction_generator.generator --rate 5000 --seconds 30 --fraud-ratio 0.1
```

---

## View Results

```powershell
# Check new alerts
docker compose exec postgres psql -U fraud -d fraud -c "SELECT COUNT(*) FROM alerts;"

# View dashboards
start http://localhost:5173
```

---

## STOP System

```powershell
# Stop all services (keeps data)
docker compose down

# Stop and delete data (WARNING: deletes everything)
docker compose down -v
```

---

Done! 🎉

