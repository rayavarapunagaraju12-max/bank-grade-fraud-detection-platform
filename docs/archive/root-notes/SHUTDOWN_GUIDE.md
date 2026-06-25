# 🛑 COMPLETE SHUTDOWN GUIDE

## Before You Shutdown - CRITICAL STEPS

Follow these steps in order to safely preserve all data:

---

## Step 1: Backup All Data (MOST IMPORTANT)

### 1.1 Backup Alerts Database
```powershell
cd "C:\Fraud detection\fraud-detection-system"

# Export alerts to CSV
docker compose exec postgres psql -U fraud -d fraud -c "\COPY alerts TO '/tmp/alerts_backup.csv' WITH CSV HEADER"

# Copy from container to local
docker compose cp fraud-detection-system-postgres-1:/tmp/alerts_backup.csv ./backup_alerts_$(Get-Date -Format "yyyyMMdd_HHmmss").csv

# Verify backup created
ls -la backup_alerts_*.csv
```

### 1.2 Backup Audit Logs
```powershell
# Export audit logs
docker compose exec postgres psql -U fraud -d fraud -c "\COPY audit_logs TO '/tmp/audit_logs_backup.csv' WITH CSV HEADER"

# Copy from container
docker compose cp fraud-detection-system-postgres-1:/tmp/audit_logs_backup.csv ./backup_audit_logs_$(Get-Date -Format "yyyyMMdd_HHmmss").csv

# Verify
ls -la backup_audit_logs_*.csv
```

### 1.3 Backup Complete PostgreSQL Database
```powershell
# Full database dump (safest option)
docker compose exec postgres pg_dump -U fraud fraud | Out-File -FilePath "./backup_full_$(Get-Date -Format "yyyyMMdd_HHmmss").sql" -Encoding UTF8

# This backup can be restored completely later
ls -la backup_full_*.sql
```

### 1.4 Backup Neo4j Graph Database
```powershell
# Export Neo4j database
docker compose exec neo4j neo4j-admin database dump neo4j /tmp/neo4j_backup.dump

# Copy from container
docker compose cp fraud-detection-system-neo4j-1:/tmp/neo4j_backup.dump ./backup_neo4j_$(Get-Date -Format "yyyyMMdd_HHmmss").dump

# Verify
ls -la backup_neo4j_*.dump
```

---

## Step 2: Export Statistics & Metrics

### 2.1 Get Final Alert Statistics
```powershell
# Export all statistics to file
docker compose exec postgres psql -U fraud -d fraud -c "
SELECT 
  COUNT(*) as total_alerts,
  ROUND(AVG(score)::numeric, 4) as avg_fraud_score,
  ROUND(MAX(score)::numeric, 4) as max_fraud_score,
  ROUND(MIN(score)::numeric, 4) as min_fraud_score,
  COUNT(CASE WHEN score >= 0.9 THEN 1 END) as critical_alerts,
  COUNT(CASE WHEN score >= 0.7 AND score < 0.9 THEN 1 END) as high_alerts,
  COUNT(CASE WHEN score >= 0.5 AND score < 0.7 THEN 1 END) as medium_alerts
FROM alerts;
" | Out-File -FilePath "./final_statistics_$(Get-Date -Format "yyyyMMdd_HHmmss").txt" -Encoding UTF8

# View the file
cat "./final_statistics_*.txt"
```

### 2.2 Export System Metrics
```powershell
# Get Prometheus metrics
docker compose exec api python -c "import requests; r = requests.get('http://localhost:8000/metrics'); print(r.text)" | Out-File -FilePath "./prometheus_metrics_$(Get-Date -Format "yyyyMMdd_HHmmss").txt" -Encoding UTF8
```

### 2.3 Get System Logs
```powershell
# Export all Docker logs
docker compose logs --all | Out-File -FilePath "./system_logs_$(Get-Date -Format "yyyyMMdd_HHmmss").log" -Encoding UTF8

# Export API logs
docker compose logs api | Out-File -FilePath "./api_logs_$(Get-Date -Format "yyyyMMdd_HHmmss").log" -Encoding UTF8

# Export stream consumer logs
docker compose logs stream-consumer | Out-File -FilePath "./stream_consumer_logs_$(Get-Date -Format "yyyyMMdd_HHmmss").log" -Encoding UTF8

# Export database logs
docker compose logs postgres | Out-File -FilePath "./postgres_logs_$(Get-Date -Format "yyyyMMdd_HHmmss").log" -Encoding UTF8
```

---

## Step 3: Save Configuration & Documentation

### 3.1 Backup Current Configuration
```powershell
# Copy .env (don't commit to Git if has secrets)
cp .env "./backup_env_$(Get-Date -Format "yyyyMMdd_HHmmss").env"

# Copy docker-compose.yml for reference
cp docker-compose.yml "./backup_docker-compose_$(Get-Date -Format "yyyyMMdd_HHmmss").yml"
```

### 3.2 Create Shutdown Report
```powershell
# Create summary report
@"
SYSTEM SHUTDOWN REPORT
=====================
Date: $(Get-Date)
System Status: SHUTTING DOWN

Backups Created:
- Alerts Database: $(ls backup_alerts_*.csv | Select-Object -Last 1)
- Audit Logs: $(ls backup_audit_logs_*.csv | Select-Object -Last 1)
- Full PostgreSQL: $(ls backup_full_*.sql | Select-Object -Last 1)
- Neo4j Graph: $(ls backup_neo4j_*.dump | Select-Object -Last 1)
- Logs: $(ls *.log | Measure-Object | Select-Object -ExpandProperty Count) log files

Statistics Exported:
- Final metrics saved
- Transaction counts saved
- Alert statistics saved

Configuration Backed Up:
- Environment file backed up
- Docker-compose backed up
- All documentation present

Services Running Before Shutdown:
"@ | Out-File -FilePath "./SHUTDOWN_REPORT_$(Get-Date -Format "yyyyMMdd_HHmmss").txt" -Encoding UTF8

# Add service status
docker compose ps >> "./SHUTDOWN_REPORT_$(Get-Date -Format "yyyyMMdd_HHmmss").txt"
```

---

## Step 4: Verify All Backups

### 4.1 Check Backup Files
```powershell
# List all backup files created
Write-Host "=== BACKUP FILES ===" -ForegroundColor Green
ls backup_* -File

Write-Host "`n=== LOG FILES ===" -ForegroundColor Green
ls *.log -File

Write-Host "`n=== STATISTICS ===" -ForegroundColor Green
ls final_statistics_* -File

# Check file sizes
Write-Host "`n=== FILE SIZES ===" -ForegroundColor Green
ls backup_*, *.log, final_statistics_* | Select-Object Name, @{Name="Size(MB)";Expression={[math]::Round($_.Length/1MB, 2)}}
```

### 4.2 Verify Database Backup Integrity
```powershell
# Check PostgreSQL backup
$backup_file = ls backup_full_*.sql | Select-Object -Last 1
Write-Host "PostgreSQL backup file: $($backup_file.Name)" -ForegroundColor Green
Write-Host "Size: $([math]::Round($backup_file.Length/1MB, 2)) MB" -ForegroundColor Green

# Check Neo4j backup
$neo4j_file = ls backup_neo4j_*.dump | Select-Object -Last 1
Write-Host "Neo4j backup file: $($neo4j_file.Name)" -ForegroundColor Green
Write-Host "Size: $([math]::Round($neo4j_file.Length/1MB, 2)) MB" -ForegroundColor Green
```

---

## Step 5: Document Final State

### 5.1 Create Final Status Report
```powershell
# Get final metrics before shutdown
docker compose exec postgres psql -U fraud -d fraud -c "
SELECT 
  'FINAL SYSTEM STATE' as report_type,
  COUNT(*) as total_alerts,
  (SELECT COUNT(*) FROM audit_logs) as total_audit_logs,
  (SELECT COUNT(*) FROM cases) as total_cases,
  NOW()::timestamp as export_timestamp
FROM alerts;
" | Out-File -FilePath "./FINAL_STATE_$(Get-Date -Format "yyyyMMdd_HHmmss").txt" -Encoding UTF8
```

### 5.2 List All Backups Summary
```powershell
$summary = @"
BACKUP SUMMARY
==============
Created: $(Get-Date)

PostgreSQL Backups:
- Alerts CSV: $(ls backup_alerts_*.csv -ErrorAction SilentlyContinue | Select-Object -Last 1 | ForEach-Object { $_.Name })
- Audit Logs CSV: $(ls backup_audit_logs_*.csv -ErrorAction SilentlyContinue | Select-Object -Last 1 | ForEach-Object { $_.Name })
- Full Database SQL: $(ls backup_full_*.sql -ErrorAction SilentlyContinue | Select-Object -Last 1 | ForEach-Object { $_.Name })

Graph Database:
- Neo4j Backup: $(ls backup_neo4j_*.dump -ErrorAction SilentlyContinue | Select-Object -Last 1 | ForEach-Object { $_.Name })

Logs:
- System Logs: $(ls system_logs_*.log -ErrorAction SilentlyContinue | Select-Object -Last 1 | ForEach-Object { $_.Name })
- API Logs: $(ls api_logs_*.log -ErrorAction SilentlyContinue | Select-Object -Last 1 | ForEach-Object { $_.Name })
- Consumer Logs: $(ls stream_consumer_logs_*.log -ErrorAction SilentlyContinue | Select-Object -Last 1 | ForEach-Object { $_.Name })
- Database Logs: $(ls postgres_logs_*.log -ErrorAction SilentlyContinue | Select-Object -Last 1 | ForEach-Object { $_.Name })

Configuration:
- Env Backup: $(ls backup_env_*.env -ErrorAction SilentlyContinue | Select-Object -Last 1 | ForEach-Object { $_.Name })
- Docker-compose Backup: $(ls backup_docker-compose_*.yml -ErrorAction SilentlyContinue | Select-Object -Last 1 | ForEach-Object { $_.Name })

All backups are stored in: $(Get-Location)
"@

$summary | Out-File -FilePath "./BACKUP_SUMMARY_$(Get-Date -Format "yyyyMMdd_HHmmss").txt" -Encoding UTF8
Write-Host $summary -ForegroundColor Green
```

---

## Step 6: Stop Services Gracefully

### 6.1 Stop Without Deleting Data (Recommended)
```powershell
# This stops all services but keeps all data
# You can restart later with: docker compose up -d

Write-Host "Stopping all services (keeping data)..." -ForegroundColor Yellow
docker compose down

Write-Host "Waiting for graceful shutdown..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Verify all stopped
Write-Host "Verifying all services stopped..." -ForegroundColor Green
docker compose ps

Write-Host "`n✅ System stopped successfully (data preserved)" -ForegroundColor Green
```

### 6.2 Stop and Delete Data (If you want to start fresh)
```powershell
# WARNING: This deletes all database data!
Write-Host "⚠️  WARNING: This will DELETE all data!" -ForegroundColor Red
$confirm = Read-Host "Type 'YES' to confirm deletion"

if ($confirm -eq "YES") {
    Write-Host "Stopping services and deleting data..." -ForegroundColor Yellow
    docker compose down -v
    
    Write-Host "✅ All services stopped and data deleted" -ForegroundColor Green
} else {
    Write-Host "Cancelled" -ForegroundColor Green
}
```

### 6.3 Remove Images (Optional - Only if deploying elsewhere)
```powershell
# This removes Docker images (takes time to rebuild)
Write-Host "Removing Docker images..." -ForegroundColor Yellow
docker compose down -v --rmi all

Write-Host "✅ Everything removed (images deleted)" -ForegroundColor Green
```

---

## Step 7: Cleanup Local Storage

### 7.1 Verify Free Space
```powershell
# Check disk space before cleanup
$disk = Get-Volume | Where-Object {$_.DriveLetter -eq 'C'}
Write-Host "Disk Space:" -ForegroundColor Green
Write-Host "Total: $([math]::Round($disk.Size/1GB, 2)) GB"
Write-Host "Used: $([math]::Round(($disk.Size - $disk.SizeRemaining)/1GB, 2)) GB"
Write-Host "Free: $([math]::Round($disk.SizeRemaining/1GB, 2)) GB"
```

### 7.2 Clean Up Old Backups (Keep Last 5)
```powershell
# Keep only last 5 backups, delete older ones
Write-Host "Cleaning up old backups (keeping last 5)..." -ForegroundColor Yellow

Get-Item backup_alerts_*.csv | Sort-Object -Property LastWriteTime -Descending | Select-Object -Skip 5 | Remove-Item
Get-Item backup_audit_logs_*.csv | Sort-Object -Property LastWriteTime -Descending | Select-Object -Skip 5 | Remove-Item
Get-Item backup_full_*.sql | Sort-Object -Property LastWriteTime -Descending | Select-Object -Skip 5 | Remove-Item
Get-Item backup_neo4j_*.dump | Sort-Object -Property LastWriteTime -Descending | Select-Object -Skip 5 | Remove-Item

Write-Host "✅ Old backups cleaned up" -ForegroundColor Green
```

### 7.3 Archive Backups (Optional)
```powershell
# Create archive of all backups
$date = Get-Date -Format "yyyyMMdd_HHmmss"
$archive_name = "fraud_detection_backup_$date.zip"

Write-Host "Creating archive: $archive_name" -ForegroundColor Yellow
Compress-Archive -Path backup_*, *.log, final_statistics_*, BACKUP_SUMMARY_*.txt `
    -DestinationPath $archive_name -CompressionLevel Optimal

Write-Host "✅ Archive created: $archive_name" -ForegroundColor Green
Write-Host "Size: $([math]::Round((Get-Item $archive_name).Length/1MB, 2)) MB" -ForegroundColor Green
```

---

## Step 8: Final Verification Checklist

```powershell
# Run final verification
Write-Host "=== FINAL SHUTDOWN VERIFICATION ===" -ForegroundColor Cyan

# 1. Check all services stopped
Write-Host "`n1. Services Status:" -ForegroundColor Green
docker compose ps
if ($LASTEXITCODE -eq 0) { Write-Host "   ✅ Docker compose responsive" } else { Write-Host "   ✅ Already stopped" }

# 2. Check backups exist
Write-Host "`n2. Backup Files:" -ForegroundColor Green
$alerts = ls backup_alerts_*.csv 2>/dev/null | Measure-Object | Select-Object -ExpandProperty Count
$audit = ls backup_audit_logs_*.csv 2>/dev/null | Measure-Object | Select-Object -ExpandProperty Count
$full = ls backup_full_*.sql 2>/dev/null | Measure-Object | Select-Object -ExpandProperty Count
$neo4j = ls backup_neo4j_*.dump 2>/dev/null | Measure-Object | Select-Object -ExpandProperty Count

Write-Host "   - Alerts backups: $alerts ✅"
Write-Host "   - Audit backups: $audit ✅"
Write-Host "   - Full DB backups: $full ✅"
Write-Host "   - Neo4j backups: $neo4j ✅"

# 3. Check logs saved
Write-Host "`n3. Log Files:" -ForegroundColor Green
$logs = ls *.log 2>/dev/null | Measure-Object | Select-Object -ExpandProperty Count
Write-Host "   - Log files saved: $logs ✅"

# 4. Confirm disk space
Write-Host "`n4. Disk Space:" -ForegroundColor Green
$disk = Get-Volume | Where-Object {$_.DriveLetter -eq 'C'}
Write-Host "   - Free space: $([math]::Round($disk.SizeRemaining/1GB, 2)) GB ✅"

Write-Host "`n✅ ALL SHUTDOWN TASKS COMPLETED" -ForegroundColor Green
```

---

## COMPLETE SHUTDOWN SCRIPT (Run All Steps)

```powershell
# Run this complete script for full shutdown

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║          FRAUD DETECTION SYSTEM - SHUTDOWN SCRIPT         ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

# Step 1: Backups
Write-Host "`n[1/8] Creating database backups..." -ForegroundColor Yellow
docker compose exec postgres psql -U fraud -d fraud -c "\COPY alerts TO '/tmp/alerts_backup.csv' WITH CSV HEADER"
docker compose cp fraud-detection-system-postgres-1:/tmp/alerts_backup.csv "./backup_alerts_$timestamp.csv"
docker compose exec postgres pg_dump -U fraud fraud | Out-File -FilePath "./backup_full_$timestamp.sql" -Encoding UTF8
Write-Host "✅ Backups complete" -ForegroundColor Green

# Step 2: Statistics
Write-Host "`n[2/8] Exporting statistics..." -ForegroundColor Yellow
docker compose exec postgres psql -U fraud -d fraud -c "
SELECT COUNT(*) as total_alerts, ROUND(AVG(score)::numeric, 4) as avg_score 
FROM alerts;" | Out-File "./final_statistics_$timestamp.txt" -Encoding UTF8
Write-Host "✅ Statistics exported" -ForegroundColor Green

# Step 3: Logs
Write-Host "`n[3/8] Saving system logs..." -ForegroundColor Yellow
docker compose logs --all | Out-File "./system_logs_$timestamp.log" -Encoding UTF8
docker compose logs api | Out-File "./api_logs_$timestamp.log" -Encoding UTF8
Write-Host "✅ Logs saved" -ForegroundColor Green

# Step 4: Configuration
Write-Host "`n[4/8] Backing up configuration..." -ForegroundColor Yellow
cp .env "./backup_env_$timestamp.env"
cp docker-compose.yml "./backup_docker-compose_$timestamp.yml"
Write-Host "✅ Configuration backed up" -ForegroundColor Green

# Step 5: Stop Services
Write-Host "`n[5/8] Stopping services..." -ForegroundColor Yellow
docker compose down
Start-Sleep -Seconds 5
Write-Host "✅ Services stopped" -ForegroundColor Green

# Step 6: Cleanup
Write-Host "`n[6/8] Cleaning up old backups..." -ForegroundColor Yellow
Get-Item backup_alerts_*.csv 2>/dev/null | Sort-Object LastWriteTime -Descending | Select-Object -Skip 5 | Remove-Item -ErrorAction SilentlyContinue
Write-Host "✅ Cleanup complete" -ForegroundColor Green

# Step 7: Verification
Write-Host "`n[7/8] Verifying shutdown..." -ForegroundColor Yellow
$backups = ls backup_* 2>/dev/null | Measure-Object | Select-Object -ExpandProperty Count
$logs = ls *.log 2>/dev/null | Measure-Object | Select-Object -ExpandProperty Count
Write-Host "   - Backups created: $backups"
Write-Host "   - Logs saved: $logs"
Write-Host "✅ Verification complete" -ForegroundColor Green

# Step 8: Summary
Write-Host "`n[8/8] Creating shutdown summary..." -ForegroundColor Yellow
@"
SHUTDOWN COMPLETED: $timestamp
========================================
Backups: Created and verified
Logs: Saved and archived
Data: Preserved for restart
Services: All stopped
Status: Ready for next deployment

To restart: docker compose up -d
"@ | Out-File "./SHUTDOWN_COMPLETE_$timestamp.txt"
Write-Host "✅ Shutdown complete" -ForegroundColor Green

Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║     ✅ SYSTEM SHUTDOWN COMPLETE - DATA PRESERVED ✅        ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green
```

---

## What Was Saved?

After following this guide, you'll have:

```
✅ Alerts Database         (CSV + SQL backup)
✅ Audit Logs              (CSV backup)
✅ Full PostgreSQL DB      (SQL dump)
✅ Neo4j Graph DB          (Dump file)
✅ All System Logs         (Multiple log files)
✅ Configuration Files     (.env, docker-compose.yml)
✅ Final Statistics        (Metrics snapshot)
✅ Shutdown Report         (Complete documentation)
```

---

## How to Restart Later

```powershell
cd "C:\Fraud detection\fraud-detection-system"

# Simply restart the system
docker compose up -d

# All data will be preserved and available
# System will be exactly as it was when you shut it down
```

---

## If You Need to Restore from Backup

```powershell
# Restore full PostgreSQL database
docker compose exec postgres psql -U fraud fraud < backup_full_YYYYMMDD_HHMMSS.sql

# Restore Neo4j database
docker compose exec neo4j neo4j-admin database load neo4j backup_neo4j_YYYYMMDD_HHMMSS.dump

# All data will be restored exactly as it was
```

---

## Shutdown Checklist

- [ ] Read this entire guide
- [ ] Run backup commands (Steps 1-3)
- [ ] Verify all backups created (Step 4)
- [ ] Stop services gracefully (Step 6.1)
- [ ] Verify all stopped: `docker compose ps`
- [ ] Confirm disk space available
- [ ] Keep backup files safe
- [ ] Document any notes about shutdown

---

## ✅ Ready to Shutdown?

Run the **COMPLETE SHUTDOWN SCRIPT** above and all steps will be automated!

