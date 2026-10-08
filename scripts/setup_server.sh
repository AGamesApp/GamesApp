#!/bin/bash
# ==============================================================================
# AGames Server Setup Script for Hetzner CPX22
# ==============================================================================
# This script automates the initial server setup process
# Run as root: bash setup_server.sh
# ==============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_USER="agames"
APP_DIR="/var/www/agames"
PYTHON_VERSION="3.11"

# Functions
print_status() {
    echo -e "${GREEN}==>${NC} $1"
}

print_error() {
    echo -e "${RED}ERROR:${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}WARNING:${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    print_error "Please run as root (use sudo)"
    exit 1
fi

print_status "Starting AGames server setup for Hetzner CPX22..."

# Update system
print_status "Updating system packages..."
apt update && apt upgrade -y

# Set timezone
print_status "Setting timezone to UTC..."
timedatectl set-timezone UTC

# Install essential packages
print_status "Installing essential packages..."
apt install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    python3.11-dev \
    build-essential \
    libpq-dev \
    curl \
    git \
    wget \
    software-properties-common \
    htop \
    ncdu \
    iotop

# Install PostgreSQL
print_status "Installing PostgreSQL 14..."
apt install -y postgresql postgresql-contrib

# Install Redis
print_status "Installing Redis..."
apt install -y redis-server

# Install Nginx
print_status "Installing Nginx..."
apt install -y nginx

# Configure firewall
print_status "Configuring firewall..."
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
echo "y" | ufw enable

# Create application user
print_status "Creating application user: $APP_USER..."
if id "$APP_USER" &>/dev/null; then
    print_warning "User $APP_USER already exists"
else
    adduser --disabled-password --gecos "" $APP_USER
    usermod -aG sudo $APP_USER
    print_status "User $APP_USER created"
fi

# Create application directory
print_status "Creating application directory..."
mkdir -p $APP_DIR
chown -R $APP_USER:$APP_USER $APP_DIR

# Setup PostgreSQL database
print_status "Setting up PostgreSQL database..."
read -p "Enter PostgreSQL database name [agames_db]: " DB_NAME
DB_NAME=${DB_NAME:-agames_db}

read -p "Enter PostgreSQL username [agames_user]: " DB_USER
DB_USER=${DB_USER:-agames_user}

read -sp "Enter PostgreSQL password: " DB_PASS
echo

# Create database and user
sudo -u postgres psql <<EOF
CREATE DATABASE $DB_NAME;
CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';
ALTER ROLE $DB_USER SET client_encoding TO 'utf8';
ALTER ROLE $DB_USER SET default_transaction_isolation TO 'read committed';
ALTER ROLE $DB_USER SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
\q
EOF

print_status "PostgreSQL database created: $DB_NAME"

# Configure PostgreSQL for CPX22
print_status "Optimizing PostgreSQL configuration for CPX22..."
cp /etc/postgresql/14/main/postgresql.conf /etc/postgresql/14/main/postgresql.conf.backup

cat >> /etc/postgresql/14/main/postgresql.conf <<EOF

# AGames Optimization for CPX22 (3 vCPU, 4GB RAM)
max_connections = 100
shared_buffers = 1GB
effective_cache_size = 3GB
maintenance_work_mem = 256MB
work_mem = 10MB
wal_buffers = 16MB
max_wal_size = 1GB
checkpoint_completion_target = 0.9
random_page_cost = 1.1
effective_io_concurrency = 200
max_worker_processes = 3
max_parallel_workers_per_gather = 2
max_parallel_workers = 3
log_min_duration_statement = 1000
EOF

systemctl restart postgresql
print_status "PostgreSQL optimized and restarted"

# Configure Redis for CPX22
print_status "Optimizing Redis configuration for CPX22..."
cp /etc/redis/redis.conf /etc/redis/redis.conf.backup

# Update Redis config
sed -i 's/# maxmemory <bytes>/maxmemory 256mb/' /etc/redis/redis.conf
sed -i 's/# maxmemory-policy noeviction/maxmemory-policy allkeys-lru/' /etc/redis/redis.conf

systemctl restart redis-server
print_status "Redis optimized and restarted"

# Install Certbot for SSL
print_status "Installing Certbot for SSL certificates..."
apt install -y certbot python3-certbot-nginx

# Enable services
print_status "Enabling services to start on boot..."
systemctl enable postgresql
systemctl enable redis-server
systemctl enable nginx

# Create backup directory
print_status "Creating backup directory..."
mkdir -p /var/backups/agames
chown -R $APP_USER:$APP_USER /var/backups/agames

# Print summary
print_status "Server setup completed successfully!"
echo ""
echo -e "${GREEN}=== Setup Summary ===${NC}"
echo "• Application User: $APP_USER"
echo "• Application Directory: $APP_DIR"
echo "• Database Name: $DB_NAME"
echo "• Database User: $DB_USER"
echo "• Python Version: $PYTHON_VERSION"
echo "• PostgreSQL: Installed and optimized for CPX22"
echo "• Redis: Installed and optimized for CPX22"
echo "• Nginx: Installed"
echo "• Firewall: Configured (ports 22, 80, 443)"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Switch to application user: su - $APP_USER"
echo "2. Clone your repository to $APP_DIR"
echo "3. Run deployment script: bash $APP_DIR/scripts/deploy.sh"
echo ""
echo -e "${GREEN}Save these credentials:${NC}"
echo "DATABASE_URL=postgresql://$DB_USER:$DB_PASS@localhost:5432/$DB_NAME"
echo ""
