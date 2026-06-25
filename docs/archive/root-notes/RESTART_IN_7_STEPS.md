# 🚀 RESTART IN 7 SIMPLE STEPS

## Copy & Paste These Commands One By One

---

## ⏱️ TAKES 5-7 MINUTES TOTAL

---

### STEP 1️⃣ (5 seconds)
```powershell
cd "C:\Fraud detection\fraud-detection-system"
```
✅ Now you're in the project folder

---

### STEP 2️⃣ (3-5 minutes) ⏱️ LONGEST STEP
```powershell
docker compose up -d --build
```
**Wait for this to complete. You'll see:**
```
[+] Running 15/15
✔ Container fraud-detection-system-api-1 Started
...
```

✅ All services are starting

---

### STEP 3️⃣ (5 seconds)
```powershell
docker compose ps
```

✅ Check you see all 15 services with "Up" status

---

### STEP 4️⃣ (30 seconds) ⏱️ WAIT
```powershell
Start-Sleep -Seconds 30
```

✅ Wait for services to fully initialize

---

### STEP 5️⃣ (5 seconds)
```powershell
docker compose exec postgres psql -U fraud -d fraud -c "SELECT COUNT(*) FROM alerts;"
```

**Expected:** Should show ~55,000 alerts

✅ Your data is restored!

---

### STEP 6️⃣ (5 seconds)
```powershell
docker compose exec api python -c "import requests; print(requests.get('http://localhost:8000/health').json())"
```

**Expected:** Should return `{'status': 'ok', ...}`

✅ API is healthy!

---

### STEP 7️⃣ (5 seconds)
```powershell
start http://localhost:5173
```

✅ Dashboard opens in browser!

---

## 🎉 DONE! 

Your fraud detection system is running with all data restored!

---

## OPTIONAL: View All Dashboards

```powershell
# Open all dashboards
start http://localhost:5173      # Fraud Alerts
start http://localhost:3000      # Grafana
start http://localhost:7474      # Neo4j
start http://localhost:8000/docs # API Docs
start http://localhost:5601      # Kibana
start http://localhost:9090      # Prometheus
```

---

## STOP SYSTEM

```powershell
# Stop (keeps data)
docker compose down

# Stop and delete data
docker compose down -v
```

---

## IF SOMETHING GOES WRONG

Check logs:
```powershell
docker compose logs -f
```

Restart a service:
```powershell
docker compose restart postgres
```

Full restart:
```powershell
docker compose down
docker compose up -d --build
```

---

## ✅ THAT'S ALL YOU NEED!

All 15 services running with all data restored!

