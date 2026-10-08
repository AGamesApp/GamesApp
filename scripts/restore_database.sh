#!/bin/bash
#
# PostgreSQL Database Restore Script for AGames
# Restore from backup file
#

# Configuration
DB_NAME="agames_db"
DB_USER="agames_user"
BACKUP_DIR="/root/backups/postgresql"
LOG_FILE="${BACKUP_DIR}/restore.log"

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "${LOG_FILE}"
}

# Check if backup file is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <backup_file.sql.gz>"
    echo ""
    echo "Available backups:"
    ls -lh "${BACKUP_DIR}"/agames_backup_*.sql.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

BACKUP_FILE="$1"

# Check if backup file exists
if [ ! -f "${BACKUP_FILE}" ]; then
    echo "ERROR: Backup file not found: ${BACKUP_FILE}"
    exit 1
fi

# Confirm restoration
echo "WARNING: This will restore the database from backup."
echo "Backup file: ${BACKUP_FILE}"
echo "Target database: ${DB_NAME}"
echo ""
read -p "Are you sure you want to continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Restore cancelled."
    exit 0
fi

log_message "Starting database restore from ${BACKUP_FILE}"

# Create a backup of current state before restore
CURRENT_BACKUP="${BACKUP_DIR}/pre_restore_backup_$(date +%Y%m%d_%H%M%S).sql.gz"
log_message "Creating backup of current state: ${CURRENT_BACKUP}"
sudo -u postgres pg_dump "${DB_NAME}" | gzip > "${CURRENT_BACKUP}" 2>> "${LOG_FILE}"

# Decompress backup file
TEMP_SQL="/tmp/restore_temp_$(date +%Y%m%d_%H%M%S).sql"
log_message "Decompressing backup file"
gunzip -c "${BACKUP_FILE}" > "${TEMP_SQL}" 2>> "${LOG_FILE}"

if [ $? -ne 0 ]; then
    log_message "ERROR: Failed to decompress backup file"
    rm -f "${TEMP_SQL}"
    exit 1
fi

# Drop existing connections
log_message "Terminating existing database connections"
sudo -u postgres psql -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '${DB_NAME}' AND pid <> pg_backend_pid();" 2>> "${LOG_FILE}"

# Drop and recreate database
log_message "Dropping existing database"
sudo -u postgres psql -c "DROP DATABASE IF EXISTS ${DB_NAME};" 2>> "${LOG_FILE}"

log_message "Creating fresh database"
sudo -u postgres psql -c "CREATE DATABASE ${DB_NAME} OWNER ${DB_USER};" 2>> "${LOG_FILE}"

# Restore from backup
log_message "Restoring database from backup"
if sudo -u postgres psql "${DB_NAME}" < "${TEMP_SQL}" 2>> "${LOG_FILE}"; then
    log_message "Database restored successfully"
    rm -f "${TEMP_SQL}"
    
    # Verify restoration
    TABLE_COUNT=$(sudo -u postgres psql -d "${DB_NAME}" -t -c "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';")
    log_message "Tables restored: ${TABLE_COUNT}"
    
    echo ""
    echo "✅ Database restored successfully!"
    echo "Pre-restore backup saved at: ${CURRENT_BACKUP}"
    exit 0
else
    log_message "ERROR: Database restore failed"
    rm -f "${TEMP_SQL}"
    echo ""
    echo "❌ Restore failed. Check log: ${LOG_FILE}"
    echo "Current state backup: ${CURRENT_BACKUP}"
    exit 1
fi
