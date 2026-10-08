#!/bin/bash
#
# Database Backup Management Script
# List, clean, and manage backups
# Auto-terminates after 5 minutes to prevent hanging
#

# Auto-timeout after 5 minutes (300 seconds)
SCRIPT_TIMEOUT=300
(
    sleep $SCRIPT_TIMEOUT
    echo "$(date): Script timeout reached - force terminating" >&2
    pkill -P $$ 2>/dev/null || true
    exit 124
) &
TIMEOUT_PID=$!
trap "kill $TIMEOUT_PID 2>/dev/null || true" EXIT

BACKUP_DIR="/root/backups/postgresql"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "==================================================="
echo "       AGames Database Backup Manager"
echo "==================================================="
echo ""

# Function to display menu
show_menu() {
    echo "Choose an option:"
    echo "1) List all backups"
    echo "2) Show disk usage"
    echo "3) Create manual backup now"
    echo "4) Clean old backups (older than 7 days)"
    echo "5) Show backup schedule (cron jobs)"
    echo "6) View backup log"
    echo "7) Exit"
    echo ""
}

# Function to list backups
list_backups() {
    echo -e "${GREEN}Available Backups:${NC}"
    echo ""
    if ls "${BACKUP_DIR}"/agames_backup_*.sql.gz 1> /dev/null 2>&1; then
        ls -lh "${BACKUP_DIR}"/agames_backup_*.sql.gz | awk '{print $9, "("$5")", $6, $7, $8}'
        echo ""
        TOTAL_SIZE=$(du -sh "${BACKUP_DIR}" | cut -f1)
        BACKUP_COUNT=$(ls -1 "${BACKUP_DIR}"/agames_backup_*.sql.gz | wc -l)
        echo -e "${YELLOW}Total backups: ${BACKUP_COUNT}${NC}"
        echo -e "${YELLOW}Total size: ${TOTAL_SIZE}${NC}"
    else
        echo "No backups found in ${BACKUP_DIR}"
    fi
    echo ""
}

# Function to show disk usage
show_disk_usage() {
    echo -e "${GREEN}Disk Usage:${NC}"
    echo ""
    df -h /root
    echo ""
    echo -e "${GREEN}Backup Directory Usage:${NC}"
    du -sh "${BACKUP_DIR}"
    echo ""
}

# Function to create manual backup
create_backup() {
    echo -e "${GREEN}Creating manual backup...${NC}"
    /root/game/scripts/backup_database.sh
    echo ""
}

# Function to clean old backups
clean_backups() {
    echo -e "${YELLOW}Cleaning backups older than 7 days...${NC}"
    BEFORE_COUNT=$(find "${BACKUP_DIR}" -name "agames_backup_*.sql.gz" -type f | wc -l)
    find "${BACKUP_DIR}" -name "agames_backup_*.sql.gz" -type f -mtime +7 -delete
    AFTER_COUNT=$(find "${BACKUP_DIR}" -name "agames_backup_*.sql.gz" -type f | wc -l)
    DELETED=$((BEFORE_COUNT - AFTER_COUNT))
    echo -e "${GREEN}Deleted ${DELETED} old backup(s)${NC}"
    echo -e "${GREEN}Remaining backups: ${AFTER_COUNT}${NC}"
    echo ""
}

# Function to show cron schedule
show_schedule() {
    echo -e "${GREEN}Backup Schedule (Cron Jobs):${NC}"
    echo ""
    crontab -l | grep -E "backup_database|AGames"
    echo ""
}

# Function to view log
view_log() {
    echo -e "${GREEN}Last 30 lines of backup log:${NC}"
    echo ""
    if [ -f "${BACKUP_DIR}/backup.log" ]; then
        tail -30 "${BACKUP_DIR}/backup.log"
    else
        echo "No log file found"
    fi
    echo ""
}

# Main loop
while true; do
    show_menu
    read -p "Enter choice [1-7]: " choice
    echo ""
    
    case $choice in
        1) list_backups ;;
        2) show_disk_usage ;;
        3) create_backup ;;
        4) clean_backups ;;
        5) show_schedule ;;
        6) view_log ;;
        7) echo "Exiting..."; exit 0 ;;
        *) echo -e "${RED}Invalid option. Please try again.${NC}"; echo "" ;;
    esac
    
    read -p "Press Enter to continue..."
    clear
done
