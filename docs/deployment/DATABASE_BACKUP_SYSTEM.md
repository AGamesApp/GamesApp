# Automated Database Backup System
**Database:** agames_db (PostgreSQL)  
**Implementation Date:** December 5, 2025  
**Status:** ✅ Active and Running

---

## Overview

Automated backup system with:
- ✅ Daily automated backups at 2:00 AM
- ✅ Weekly backups on Sundays at 3:00 AM
- ✅ 7-day retention policy (automatic cleanup)
- ✅ Compressed backups (gzip)
- ✅ Detailed logging
- ✅ Easy restore functionality
- ✅ Backup management tools

---

## Backup Schedule

### Daily Backups
- **Time:** 2:00 AM (server time - CET)
- **Frequency:** Every day
- **Retention:** 7 days
- **Location:** `/root/backups/postgresql/`
- **Naming:** `agames_backup_YYYYMMDD_HHMMSS.sql.gz`

### Weekly Backups
- **Time:** 3:00 AM on Sundays
- **Frequency:** Weekly
- **Retention:** Manual cleanup
- **Location:** `/root/backups/postgresql/`
- **Naming:** `weekly_backup_YYYYMMDD.sql.gz`

---

## Backup Location

```
/root/backups/postgresql/
├── agames_backup_20251205_011608.sql.gz  # Daily backups
├── weekly_backup_20251201.sql.gz         # Weekly backups
├── backup.log                            # Backup activity log
├── restore.log                           # Restore activity log
└── cron.log                              # Cron job log
```

---

## Scripts

### 1. Backup Script
**File:** `/root/game/scripts/backup_database.sh`

**Features:**
- Dumps entire PostgreSQL database
- Compresses with gzip
- Logs all activity
- Automatically removes old backups (7+ days)
- Returns exit code 0 on success, 1 on failure

**Usage:**
```bash
# Manual backup
/root/game/scripts/backup_database.sh

# Runs automatically via cron
```

**Output Example:**
```
[2025-12-05 01:16:08] Starting database backup for agames_db
[2025-12-05 01:16:08] Database dump completed successfully
[2025-12-05 01:16:08] Backup compressed: /root/backups/postgresql/agames_backup_20251205_011608.sql.gz
[2025-12-05 01:16:08] Backup size: 16K
[2025-12-05 01:16:08] Removing backups older than 7 days
[2025-12-05 01:16:08] Total backups retained: 1
[2025-12-05 01:16:08] Backup completed successfully
```

---

### 2. Restore Script
**File:** `/root/game/scripts/restore_database.sh`

**Features:**
- Lists available backups
- Creates pre-restore backup of current state
- Decompresses backup file
- Drops and recreates database
- Restores from backup
- Verifies restoration success

**Usage:**
```bash
# List available backups
/root/game/scripts/restore_database.sh

# Restore from specific backup
/root/game/scripts/restore_database.sh /root/backups/postgresql/agames_backup_20251205_011608.sql.gz
```

**Safety Features:**
- Requires "yes" confirmation
- Creates backup of current state before restore
- Logs all operations
- Verifies table count after restore

---

### 3. Backup Management Script
**File:** `/root/game/scripts/manage_backups.sh`

**Features:**
Interactive menu with:
1. List all backups (with sizes and dates)
2. Show disk usage
3. Create manual backup now
4. Clean old backups (older than 7 days)
5. Show backup schedule (cron jobs)
6. View backup log
7. Exit

**Usage:**
```bash
/root/game/scripts/manage_backups.sh
```

**Menu:**
```
===================================================
       AGames Database Backup Manager
===================================================

Choose an option:
1) List all backups
2) Show disk usage
3) Create manual backup now
4) Clean old backups (older than 7 days)
5) Show backup schedule (cron jobs)
6) View backup log
7) Exit
```

---

## Cron Jobs

### Installed Cron Schedule

**View:**
```bash
crontab -l
```

**Schedule:**
```cron
# Daily database backup at 2:00 AM
0 2 * * * /root/game/scripts/backup_database.sh >> /root/backups/postgresql/cron.log 2>&1

# Weekly backup on Sunday at 3:00 AM (kept separately)
0 3 * * 0 /root/game/scripts/backup_database.sh && cp /root/backups/postgresql/agames_backup_*.sql.gz /root/backups/postgresql/weekly_backup_$(date +\%Y\%m\%d).sql.gz >> /root/backups/postgresql/cron.log 2>&1
```

### Edit Cron Jobs
```bash
# Edit crontab
crontab -e

# Remove all cron jobs
crontab -r

# Reinstall from file
crontab /root/game/scripts/crontab_backup.txt
```

---

## Common Operations

### 1. Create Manual Backup
```bash
/root/game/scripts/backup_database.sh
```

### 2. List All Backups
```bash
ls -lh /root/backups/postgresql/agames_backup_*.sql.gz
```

### 3. Restore from Backup
```bash
# Step 1: List available backups
/root/game/scripts/restore_database.sh

# Step 2: Choose and restore
/root/game/scripts/restore_database.sh /root/backups/postgresql/agames_backup_20251205_011608.sql.gz
```

### 4. View Backup Logs
```bash
# Recent backup log
tail -30 /root/backups/postgresql/backup.log

# Cron job log
tail -30 /root/backups/postgresql/cron.log

# Restore log
tail -30 /root/backups/postgresql/restore.log
```

### 5. Check Backup Size
```bash
# Individual backup
ls -lh /root/backups/postgresql/agames_backup_20251205_011608.sql.gz

# Total backup directory
du -sh /root/backups/postgresql/
```

### 6. Clean Old Backups Manually
```bash
# Remove backups older than 7 days
find /root/backups/postgresql/ -name "agames_backup_*.sql.gz" -type f -mtime +7 -delete

# Remove backups older than 30 days
find /root/backups/postgresql/ -name "agames_backup_*.sql.gz" -type f -mtime +30 -delete
```

---

## Backup Testing

### Test Backup Integrity
```bash
# Decompress and check SQL file
gunzip -c /root/backups/postgresql/agames_backup_20251205_011608.sql.gz | head -50

# Verify backup is readable
gunzip -t /root/backups/postgresql/agames_backup_20251205_011608.sql.gz
echo $?  # Should output 0 if successful
```

### Test Restore (Dry Run)
```bash
# Decompress to temporary file
gunzip -c /root/backups/postgresql/agames_backup_20251205_011608.sql.gz > /tmp/test_restore.sql

# Check SQL content
head -20 /tmp/test_restore.sql

# Count tables in backup
grep "CREATE TABLE" /tmp/test_restore.sql | wc -l

# Cleanup
rm /tmp/test_restore.sql
```

---

## Monitoring

### Check Cron Status
```bash
# Verify cron service is running
sudo systemctl status cron

# View recent cron activity
grep CRON /var/log/syslog | tail -20
```

### Monitor Backup Success
```bash
# Check last backup
ls -lt /root/backups/postgresql/agames_backup_*.sql.gz | head -1

# Verify backup was created today
find /root/backups/postgresql/ -name "agames_backup_*.sql.gz" -type f -mtime -1

# Check backup log for errors
grep -i error /root/backups/postgresql/backup.log
```

### Alert on Backup Failure
Add to cron for email alerts:
```cron
MAILTO=your-email@example.com
0 2 * * * /root/game/scripts/backup_database.sh >> /root/backups/postgresql/cron.log 2>&1 || echo "Backup failed on $(date)" | mail -s "AGames Backup Failed" your-email@example.com
```

---

## Disaster Recovery

### Complete System Recovery

**Step 1: Install fresh system**
```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql

# Create database and user
sudo -u postgres createdb agames_db
sudo -u postgres createuser agames_user
sudo -u postgres psql -c "ALTER USER agames_user WITH PASSWORD 'AGames@pp#2025';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE agames_db TO agames_user;"
```

**Step 2: Restore from backup**
```bash
# Copy backup to server
scp backup.sql.gz root@152.53.206.21:/root/backups/postgresql/

# Restore
/root/game/scripts/restore_database.sh /root/backups/postgresql/backup.sql.gz
```

**Step 3: Verify restoration**
```bash
# Check database
sudo -u postgres psql -d agames_db -c "SELECT count(*) FROM games_game;"

# Restart services
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

---

## Off-Site Backup

### Option 1: Cloud Storage (Recommended)

**Using rclone (AWS S3, Google Drive, Backblaze B2):**
```bash
# Install rclone
sudo apt install rclone

# Configure
rclone config

# Sync backups to cloud
rclone sync /root/backups/postgresql/ remote:agames-backups/
```

**Add to cron:**
```cron
# Upload to cloud after daily backup
30 2 * * * rclone sync /root/backups/postgresql/ remote:agames-backups/ >> /root/backups/postgresql/cloud_sync.log 2>&1
```

### Option 2: Remote Server (SCP)

**Script example:**
```bash
#!/bin/bash
# Copy latest backup to remote server
LATEST_BACKUP=$(ls -t /root/backups/postgresql/agames_backup_*.sql.gz | head -1)
scp "$LATEST_BACKUP" backup-user@backup-server.com:/backups/agames/
```

### Option 3: FTP/SFTP
```bash
# Using lftp
lftp -c "open -u username,password ftp.example.com; put /root/backups/postgresql/agames_backup_*.sql.gz"
```

---

## Backup Statistics

### Current Status
- ✅ **First Backup:** December 5, 2025, 01:16:08
- ✅ **Backup Size:** ~16KB (compressed)
- ✅ **Compression Ratio:** ~75% (SQL to .gz)
- ✅ **Retention:** 7 days (automatic)
- ✅ **Frequency:** Daily + Weekly

### Estimated Storage
- **Daily backup:** ~16KB
- **7 days retention:** ~112KB
- **30 days retention:** ~480KB
- **1 year (if kept):** ~5.7MB

**Note:** As database grows, backup sizes will increase proportionally.

---

## Best Practices

### ✅ Implemented
1. Automated daily backups
2. Compressed storage (gzip)
3. Automatic old backup cleanup
4. Detailed logging
5. Pre-restore safety backup
6. Restoration verification

### 🔄 Recommended
1. **Off-site backups:** Copy to cloud storage (AWS S3, Backblaze B2)
2. **Backup testing:** Monthly restore test to verify integrity
3. **Monitoring:** Set up alerts for backup failures
4. **Encryption:** Encrypt backups for sensitive data
5. **Version control:** Keep multiple generations (daily, weekly, monthly)

### 📋 Checklist
- [x] Backup script created and tested
- [x] Cron jobs installed
- [x] Restore script available
- [x] Logs configured
- [x] Retention policy active
- [ ] Off-site backup configured (recommended)
- [ ] Monthly restore test scheduled (recommended)
- [ ] Email alerts configured (optional)

---

## Troubleshooting

### Backup Not Running
```bash
# Check cron service
sudo systemctl status cron

# Check crontab
crontab -l

# Check permissions
ls -la /root/game/scripts/backup_database.sh

# Manual test
/root/game/scripts/backup_database.sh
```

### Disk Space Issues
```bash
# Check disk space
df -h /root

# Check backup directory size
du -sh /root/backups/postgresql/

# Clean old backups
find /root/backups/postgresql/ -name "agames_backup_*.sql.gz" -type f -mtime +30 -delete
```

### Restore Failing
```bash
# Check backup integrity
gunzip -t /root/backups/postgresql/agames_backup_*.sql.gz

# Check PostgreSQL status
sudo systemctl status postgresql

# View restore log
cat /root/backups/postgresql/restore.log
```

---

## Security Considerations

### File Permissions
```bash
# Backup directory (root only)
chmod 700 /root/backups/postgresql/

# Backup files (read/write by root only)
chmod 600 /root/backups/postgresql/*.sql.gz

# Scripts (executable by root only)
chmod 700 /root/game/scripts/backup_database.sh
chmod 700 /root/game/scripts/restore_database.sh
```

### Encryption (Optional)
```bash
# Encrypt backup
gpg --symmetric --cipher-algo AES256 backup.sql.gz

# Decrypt backup
gpg --decrypt backup.sql.gz.gpg > backup.sql.gz
```

---

## Quick Reference

### Commands
```bash
# Backup
/root/game/scripts/backup_database.sh

# Restore
/root/game/scripts/restore_database.sh [backup_file.sql.gz]

# Manage
/root/game/scripts/manage_backups.sh

# List backups
ls -lh /root/backups/postgresql/

# View logs
tail -f /root/backups/postgresql/backup.log

# Check cron
crontab -l
```

---

**Last Updated:** December 5, 2025  
**Status:** ✅ Fully Operational  
**Next Backup:** Daily at 2:00 AM CET
