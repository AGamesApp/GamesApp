#!/bin/bash
# ==============================================================================
# AGames Application Deployment Script
# ==============================================================================
# This script deploys the Django application
# Run as agames user: bash deploy.sh
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
PYTHON_VERSION="python3.11"

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

print_info() {
    echo -e "${BLUE}INFO:${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    print_error "Please run as agames user (NOT root)"
    exit 1
fi

print_status "Starting AGames deployment..."

# Navigate to application directory
cd $APP_DIR

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    print_status "Creating virtual environment..."
    $PYTHON_VERSION -m venv $VENV_DIR
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source $VENV_DIR/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
print_status "Installing Python dependencies..."
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

# Check if .env file exists
if [ ! -f "$APP_DIR/.env" ]; then
    print_warning ".env file not found. Creating template..."
    
    cat > $APP_DIR/.env <<EOF
# Django Settings
SECRET_KEY='django-insecure-CHANGE_THIS_TO_STRONG_RANDOM_KEY'
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (Update with your credentials)
DATABASE_URL=postgresql://agames_user:PASSWORD@localhost:5432/agames_db

# Redis Cache
REDIS_URL=redis://127.0.0.1:6379/1
CACHE_BACKEND=django_redis.cache.RedisCache

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Gunicorn
GUNICORN_WORKERS=7

# CORS
CORS_ALLOW_ALL_ORIGINS=False
CORS_ALLOWED_ORIGINS=
EOF

    print_error ".env file created. Please edit it with your actual credentials:"
    print_info "nano $APP_DIR/.env"
    exit 1
fi

# Generate SECRET_KEY if needed
if grep -q "CHANGE_THIS_TO_STRONG_RANDOM_KEY" $APP_DIR/.env; then
    print_status "Generating SECRET_KEY..."
    NEW_SECRET=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
    sed -i "s/CHANGE_THIS_TO_STRONG_RANDOM_KEY/$NEW_SECRET/" $APP_DIR/.env
    print_status "SECRET_KEY generated"
fi

# Run migrations
print_status "Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# Collect static files
print_status "Collecting static files..."
python manage.py collectstatic --noinput

# Create media directories
print_status "Creating media directories..."
mkdir -p media/game_images media/emulator_icons
chmod -R 775 media

# Create superuser (interactive)
print_info "Do you want to create a superuser? (y/n)"
read -r CREATE_SUPERUSER
if [ "$CREATE_SUPERUSER" = "y" ]; then
    python manage.py createsuperuser
fi

# Test Gunicorn
print_status "Testing Gunicorn configuration..."
gunicorn --config gunicorn_config.py gamezone.wsgi:application --check-config

# Create Gunicorn systemd service
print_status "Creating Gunicorn systemd service..."
sudo tee /etc/systemd/system/gunicorn.service > /dev/null <<EOF
[Unit]
Description=Gunicorn daemon for AGames Django Application
After=network.target postgresql.service redis-server.service

[Service]
Type=notify
User=agames
Group=www-data
WorkingDirectory=$APP_DIR
Environment="PATH=$VENV_DIR/bin"
EnvironmentFile=$APP_DIR/.env
ExecStart=$VENV_DIR/bin/gunicorn \\
    --config $APP_DIR/gunicorn_config.py \\
    gamezone.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
print_status "Reloading systemd..."
sudo systemctl daemon-reload

# Start and enable Gunicorn
print_status "Starting Gunicorn service..."
sudo systemctl restart gunicorn
sudo systemctl enable gunicorn

# Check Gunicorn status
if sudo systemctl is-active --quiet gunicorn; then
    print_status "Gunicorn is running"
else
    print_error "Gunicorn failed to start. Check logs:"
    print_info "sudo journalctl -u gunicorn -n 50"
    exit 1
fi

# Configure Nginx
print_status "Configuring Nginx..."

# Ask for domain
print_info "Enter your domain name (or press Enter to use server IP):"
read -r DOMAIN_NAME
DOMAIN_NAME=${DOMAIN_NAME:-_}

sudo tee /etc/nginx/sites-available/agames > /dev/null <<EOF
upstream django {
    server 127.0.0.1:8000;
    keepalive 32;
}

server {
    listen 80;
    server_name $DOMAIN_NAME;
    client_max_body_size 50M;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Static files
    location /static/ {
        alias $APP_DIR/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias $APP_DIR/media/;
        expires 7d;
        add_header Cache-Control "public";
    }

    # Django application
    location / {
        proxy_pass http://django;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
        
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
}
EOF

# Enable Nginx site
sudo rm -f /etc/nginx/sites-enabled/default
sudo ln -sf /etc/nginx/sites-available/agames /etc/nginx/sites-enabled/

# Test Nginx configuration
print_status "Testing Nginx configuration..."
if sudo nginx -t; then
    print_status "Nginx configuration is valid"
    sudo systemctl restart nginx
    sudo systemctl enable nginx
else
    print_error "Nginx configuration test failed"
    exit 1
fi

# Set proper permissions
print_status "Setting file permissions..."
sudo chown -R agames:www-data $APP_DIR
sudo chmod -R 755 $APP_DIR
sudo chmod -R 775 $APP_DIR/media
sudo chmod -R 775 $APP_DIR/staticfiles

# SSL Certificate setup (optional)
if [ "$DOMAIN_NAME" != "_" ]; then
    print_info "Do you want to install SSL certificate with Let's Encrypt? (y/n)"
    read -r INSTALL_SSL
    if [ "$INSTALL_SSL" = "y" ]; then
        print_status "Installing SSL certificate..."
        sudo certbot --nginx -d $DOMAIN_NAME --non-interactive --agree-tos --redirect --email admin@$DOMAIN_NAME || true
    fi
fi

# Print deployment summary
print_status "Deployment completed successfully!"
echo ""
echo -e "${GREEN}=== Deployment Summary ===${NC}"
echo "• Application: AGames Django Backend"
echo "• Directory: $APP_DIR"
echo "• Virtual Environment: $VENV_DIR"
echo "• Python: $PYTHON_VERSION"
echo "• Gunicorn Workers: 7 (CPX22 optimized)"
echo "• Domain: $DOMAIN_NAME"
echo ""
echo -e "${GREEN}=== Service Status ===${NC}"
sudo systemctl status gunicorn --no-pager | grep "Active:"
sudo systemctl status nginx --no-pager | grep "Active:"
sudo systemctl status postgresql --no-pager | grep "Active:"
sudo systemctl status redis-server --no-pager | grep "Active:"
echo ""
echo -e "${YELLOW}=== Access Your Application ===${NC}"
if [ "$DOMAIN_NAME" != "_" ]; then
    echo "• API: http://$DOMAIN_NAME/api/"
    echo "• Admin: http://$DOMAIN_NAME/admin/"
    echo "• Docs: http://$DOMAIN_NAME/api/schema/swagger-ui/"
else
    SERVER_IP=$(curl -s ifconfig.me)
    echo "• API: http://$SERVER_IP/api/"
    echo "• Admin: http://$SERVER_IP/admin/"
    echo "• Docs: http://$SERVER_IP/api/schema/swagger-ui/"
fi
echo ""
echo -e "${YELLOW}=== Useful Commands ===${NC}"
echo "• View Gunicorn logs: sudo journalctl -u gunicorn -f"
echo "• View Nginx logs: sudo tail -f /var/log/nginx/error.log"
echo "• Restart services: sudo systemctl restart gunicorn nginx"
echo "• Check memory: free -h"
echo "• Monitor processes: htop"
echo ""
