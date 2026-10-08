#!/bin/bash
# ==============================================================================
# AGames Application Update Script
# ==============================================================================
# This script updates the deployed application with zero downtime
# Run as agames user: bash update.sh
# ==============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_DIR="/var/www/agames"
VENV_DIR="$APP_DIR/venv"

# Functions
print_status() {
    echo -e "${GREEN}==>${NC} $1"
}

print_error() {
    echo -e "${RED}ERROR:${NC} $1"
}

print_info() {
    echo -e "${BLUE}INFO:${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    print_error "Please run as agames user (NOT root)"
    exit 1
fi

print_status "Starting AGames application update..."

# Navigate to application directory
cd $APP_DIR

# Backup current version
print_status "Creating backup..."
BACKUP_DIR="/var/backups/agames"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup database
print_info "Backing up database..."
sudo -u postgres pg_dump agames_db | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup media files
print_info "Backing up media files..."
tar -czf $BACKUP_DIR/media_$DATE.tar.gz -C $APP_DIR media

# Pull latest code from git
print_status "Pulling latest code from repository..."
git fetch origin
git pull origin main  # or master, depending on your branch name

# Activate virtual environment
print_status "Activating virtual environment..."
source $VENV_DIR/bin/activate

# Install/update dependencies
print_status "Updating Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Run migrations
print_status "Running database migrations..."
python manage.py migrate --noinput

# Collect static files
print_status "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Run tests (optional)
print_info "Do you want to run tests before deploying? (y/n)"
read -r RUN_TESTS
if [ "$RUN_TESTS" = "y" ]; then
    print_status "Running tests..."
    python manage.py test || {
        print_error "Tests failed! Aborting update."
        exit 1
    }
fi

# Reload Gunicorn (zero downtime)
print_status "Reloading Gunicorn (zero downtime)..."
sudo systemctl reload gunicorn

# Wait for reload
sleep 2

# Check if Gunicorn is running
if sudo systemctl is-active --quiet gunicorn; then
    print_status "Gunicorn reloaded successfully"
else
    print_error "Gunicorn reload failed. Rolling back..."
    
    # Rollback
    git reset --hard HEAD@{1}
    sudo systemctl restart gunicorn
    
    print_error "Rolled back to previous version. Check logs:"
    print_info "sudo journalctl -u gunicorn -n 50"
    exit 1
fi

# Clear Redis cache (optional)
print_info "Do you want to clear Redis cache? (y/n)"
read -r CLEAR_CACHE
if [ "$CLEAR_CACHE" = "y" ]; then
    print_status "Clearing Redis cache..."
    redis-cli FLUSHDB
fi

# Cleanup old backups (keep last 7 days)
print_status "Cleaning up old backups..."
find $BACKUP_DIR -type f -mtime +7 -delete

# Print update summary
print_status "Application update completed successfully!"
echo ""
echo -e "${GREEN}=== Update Summary ===${NC}"
echo "• Backup created: $BACKUP_DIR/db_$DATE.sql.gz"
echo "• Code updated from git"
echo "• Dependencies updated"
echo "• Migrations applied"
echo "• Static files collected"
echo "• Gunicorn reloaded"
echo ""
echo -e "${BLUE}=== Service Status ===${NC}"
sudo systemctl status gunicorn --no-pager | grep "Active:"
echo ""
echo -e "${YELLOW}=== Verification ===${NC}"
echo "• Check application: curl http://localhost:8000/api/"
echo "• View logs: sudo journalctl -u gunicorn -f"
echo "• Check memory: free -h"
echo ""
echo -e "${GREEN}Update completed at: $(date)${NC}"
