#!/bin/bash
#
# PostgreSQL Database Backup Script for AGames
# Automated backup with rotation and compression
#

# Configuration
DB_NAME="agames_db"
DB_USER="agames_user"
BACKUP_DIR="/root/backups/postgresql"
DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/agames_backup_${DATE}.sql"
COMPRESSED_FILE="${BACKUP_FILE}.gz"
LOG_FILE="${BACKUP_DIR}/backup.log"

# Retention policy (days)
RETENTION_DAYS=7

# Create backup directory if it doesn't exist
mkdir -p "${BACKUP_DIR}"

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "${LOG_FILE}"
}

# Start backup
log_message "Starting database backup for ${DB_NAME}"

# Perform backup
if sudo -u postgres pg_dump "${DB_NAME}" > "${BACKUP_FILE}" 2>> "${LOG_FILE}"; then
    log_message "Database dump completed successfully"
    
    # Compress the backup
    if gzip "${BACKUP_FILE}" 2>> "${LOG_FILE}"; then
        log_message "Backup compressed: ${COMPRESSED_FILE}"
        
        # Get file size
        BACKUP_SIZE=$(du -h "${COMPRESSED_FILE}" | cut -f1)
        log_message "Backup size: ${BACKUP_SIZE}"
        
        # Remove old backups (keep last N days)
        log_message "Removing backups older than ${RETENTION_DAYS} days"
        find "${BACKUP_DIR}" -name "agames_backup_*.sql.gz" -type f -mtime +${RETENTION_DAYS} -delete
        
        # Count remaining backups
        BACKUP_COUNT=$(find "${BACKUP_DIR}" -name "agames_backup_*.sql.gz" -type f | wc -l)
        log_message "Total backups retained: ${BACKUP_COUNT}"
        
        log_message "Backup completed successfully: ${COMPRESSED_FILE}"
        exit 0
    else
        log_message "ERROR: Failed to compress backup"
        exit 1
    fi
else
    log_message "ERROR: Database dump failed"
    exit 1
fi
