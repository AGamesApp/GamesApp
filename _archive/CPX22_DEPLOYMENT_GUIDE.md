# AGames Deployment Guide - Hetzner CPX22
**Complete Step-by-Step Guide from Server Purchase to Running Application**

---

## 📋 Table of Contents
1. [Server Specifications](#server-specifications)
2. [Initial Server Setup](#initial-server-setup)
3. [Install System Dependencies](#install-system-dependencies)
4. [PostgreSQL Setup](#postgresql-setup)
5. [Redis Setup](#redis-setup)
6. [Application Deployment](#application-deployment)
7. [Nginx Configuration](#nginx-configuration)
8. [SSL Certificate Setup](#ssl-certificate-setup)
9. [Environment Variables](#environment-variables)
10. [Systemd Services](#systemd-services)
11. [Monitoring & Maintenance](#monitoring--maintenance)
12. [Troubleshooting](#troubleshooting)

---

## 🖥️ Server Specifications

**Hetzner CPX22 Plan**
- **CPU**: 3 vCPU AMD
- **RAM**: 4GB DDR4
- **Storage**: 80GB NVMe SSD
- **Bandwidth**: 20TB traffic
- **Price**: €10.69/month
- **Location**: Choose nearest to your users (e.g., Falkenstein, Nuremberg, Helsinki)

### Memory Allocation Plan
```
Total: 4GB RAM
├── Gunicorn Workers: 1.4GB (7 workers × 200MB)
├── PostgreSQL: 1.2GB
├── Redis: 256MB
├── Nginx: 50MB
├── Operating System: 800MB
└── Buffer/Cache: 300MB
```

---

## 🚀 Initial Server Setup

### Step 1: Purchase & Access Server

1. **Purchase Server**:
   - Go to [Hetzner Cloud Console](https://console.hetzner.cloud/)
   - Create new project: "AGames Production"
   - Add server → CPX22 → Ubuntu 22.04 LTS
   - Choose location (e.g., Falkenstein/Germany)
   - Add SSH key OR use password
   - Launch server

2. **Get Server IP**:
   ```bash
   # You'll receive an IP like: 123.45.67.89
   # Save this IP address
   ```

3. **First SSH Connection**:
   ```bash
   # From your local machine (PowerShell/CMD)
   ssh root@YOUR_SERVER_IP
   
   # Example:
   ssh root@123.45.67.89
   ```

### Step 2: Secure the Server

```bash
# Update system packages
apt update && apt upgrade -y

# Set timezone to UTC
timedatectl set-timezone UTC

# Configure firewall
ufw allow OpenSSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw enable
ufw status

# Create non-root user
adduser agames
usermod -aG sudo agames

# Copy SSH keys to new user (if using SSH keys)
rsync --archive --chown=agames:agames ~/.ssh /home/agames

# Test new user
su - agames
sudo ls  # Test sudo access
exit

# Optional: Disable root SSH login
sudo nano /etc/ssh/sshd_config
# Set: PermitRootLogin no
sudo systemctl restart sshd
```

**⚠️ IMPORTANT**: From now on, use `agames` user, NOT root!

```bash
# Exit and reconnect as agames user
exit
ssh agames@YOUR_SERVER_IP
```

---

## 📦 Install System Dependencies

```bash
# Update package list
sudo apt update

# Install Python 3.11 and essential tools
sudo apt install -y python3.11 python3.11-venv python3-pip python3.11-dev
sudo apt install -y build-essential libpq-dev curl git wget
sudo apt install -y software-properties-common

# Install PostgreSQL 14
sudo apt install -y postgresql postgresql-contrib

# Install Redis
sudo apt install -y redis-server

# Install Nginx
sudo apt install -y nginx

# Install system monitoring tools
sudo apt install -y htop ncdu iotop

# Verify installations
python3.11 --version  # Should show Python 3.11.x
psql --version        # Should show PostgreSQL 14.x
redis-cli --version   # Should show Redis 7.x
nginx -v              # Should show Nginx 1.18+
```

---

## 🐘 PostgreSQL Setup

### Step 1: Configure PostgreSQL

```bash
# Switch to postgres user
sudo -u postgres psql

# Inside psql, create database and user:
CREATE DATABASE agames_db;
CREATE USER agames_user WITH PASSWORD 'CHANGE_THIS_STRONG_PASSWORD';
ALTER ROLE agames_user SET client_encoding TO 'utf8';
ALTER ROLE agames_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE agames_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE agames_db TO agames_user;

# Exit psql
\q
```

### Step 2: Optimize PostgreSQL for CPX22

```bash
# Backup original config
sudo cp /etc/postgresql/14/main/postgresql.conf /etc/postgresql/14/main/postgresql.conf.backup

# Edit PostgreSQL config
sudo nano /etc/postgresql/14/main/postgresql.conf
```

**Add these optimizations** (or copy from `configs/postgresql_cpx22.conf`):

```conf
# CONNECTIONS
max_connections = 100

# MEMORY (Critical for 4GB RAM)
shared_buffers = 1GB                    # 25% of RAM
effective_cache_size = 3GB              # 75% of RAM
maintenance_work_mem = 256MB
work_mem = 10MB

# WAL
wal_level = replica
max_wal_size = 1GB
checkpoint_completion_target = 0.9

# PERFORMANCE (SSD optimization)
random_page_cost = 1.1
effective_io_concurrency = 200

# PARALLEL WORKERS (3 vCPU)
max_worker_processes = 3
max_parallel_workers_per_gather = 2
max_parallel_workers = 3

# LOGGING
log_min_duration_statement = 1000       # Log queries slower than 1s
```

```bash
# Restart PostgreSQL
sudo systemctl restart postgresql
sudo systemctl enable postgresql
sudo systemctl status postgresql

# Verify settings
sudo -u postgres psql -c "SHOW shared_buffers;"
sudo -u postgres psql -c "SHOW effective_cache_size;"
```

---

## 🔴 Redis Setup

### Configure Redis for CPX22

```bash
# Backup original config
sudo cp /etc/redis/redis.conf /etc/redis/redis.conf.backup

# Edit Redis config
sudo nano /etc/redis/redis.conf
```

**Key settings** (or copy from `configs/redis_cpx22.conf`):

```conf
# MEMORY LIMIT
maxmemory 256mb
maxmemory-policy allkeys-lru

# PERSISTENCE (disable RDB, use AOF)
save ""
appendonly yes
appendfsync everysec

# CONNECTIONS
maxclients 100
timeout 300

# SECURITY (uncomment and set password)
# requirepass YOUR_STRONG_REDIS_PASSWORD
```

```bash
# Restart Redis
sudo systemctl restart redis-server
sudo systemctl enable redis-server
sudo systemctl status redis-server

# Test Redis
redis-cli ping  # Should return: PONG
redis-cli INFO memory
```

---

## 🚢 Application Deployment

### Step 1: Clone Repository

```bash
# Create project directory
sudo mkdir -p /var/www/agames
sudo chown -R agames:agames /var/www/agames
cd /var/www/agames

# Clone your repository (replace with your repo URL)
git clone https://github.com/YOUR_USERNAME/agames-backend.git .

# Or upload files via SCP from your local machine:
# scp -r E:\work\game/* agames@YOUR_SERVER_IP:/var/www/agames/
```

### Step 2: Create Virtual Environment

```bash
cd /var/www/agames

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Install additional production packages
pip install gunicorn psycopg2-binary
```

### Step 3: Configure Environment Variables

```bash
# Create .env file
nano /var/www/agames/.env
```

**Add these variables** (replace with your actual values):

```env
# Django Settings
SECRET_KEY='django-insecure-CHANGE_THIS_TO_STRONG_RANDOM_KEY'
DEBUG=False
ALLOWED_HOSTS=YOUR_DOMAIN.com,YOUR_SERVER_IP,localhost

# Database
DATABASE_URL=postgresql://agames_user:CHANGE_THIS_STRONG_PASSWORD@localhost:5432/agames_db

# Redis Cache
REDIS_URL=redis://127.0.0.1:6379/1
CACHE_BACKEND=django_redis.cache.RedisCache

# Email (Gmail example)
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

# Stripe (if using payments)
STRIPE_PUBLIC_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# CORS
CORS_ALLOW_ALL_ORIGINS=False
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Gunicorn
GUNICORN_WORKERS=7
```

**Generate SECRET_KEY**:
```bash
python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### Step 4: Setup Database

```bash
# Make sure virtual environment is activated
source /var/www/agames/venv/bin/activate

cd /var/www/agames

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
# Username: admin
# Email: admin@yourdomain.com
# Password: [strong password]

# Collect static files
python manage.py collectstatic --noinput

# Create media directories
mkdir -p media/game_images media/emulator_icons
chmod -R 755 media
```

### Step 5: Test Gunicorn

```bash
# Test Gunicorn manually
gunicorn --config gunicorn_config.py gamezone.wsgi:application

# Should see:
# 🚀 Starting Gunicorn server for AGames...
# 💻 Server: Hetzner CPX22 (3 vCPU AMD, 4GB RAM)
# 📊 Configuration: 7 workers, 20 connections/worker
# 🎯 Max concurrent requests: ~140

# Press Ctrl+C to stop
```

---

## 🌐 Nginx Configuration

### Step 1: Configure Nginx

```bash
# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Create AGames site configuration
sudo nano /etc/nginx/sites-available/agames
```

**Copy this configuration** (or use `configs/nginx_cpx22.conf`):

```nginx
upstream django {
    server 127.0.0.1:8000;
    keepalive 32;
}

server {
    listen 80;
    server_name YOUR_DOMAIN.com www.YOUR_DOMAIN.com;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Static files
    location /static/ {
        alias /var/www/agames/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /var/www/agames/media/;
        expires 7d;
        add_header Cache-Control "public";
    }

    # Proxy to Gunicorn
    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/agames /etc/nginx/sites-enabled/

# Test Nginx configuration
sudo nginx -t

# If OK, restart Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
sudo systemctl status nginx
```

### Step 2: Set Permissions

```bash
# Set proper ownership
sudo chown -R agames:www-data /var/www/agames
sudo chmod -R 755 /var/www/agames

# Special permissions for media/static
sudo chmod -R 775 /var/www/agames/media
sudo chmod -R 775 /var/www/agames/staticfiles
```

---

## 🔒 SSL Certificate Setup

### Install Let's Encrypt SSL (Free)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate (replace with your domain)
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Follow prompts:
# - Enter email address
# - Agree to terms
# - Choose: Redirect HTTP to HTTPS (option 2)

# Test auto-renewal
sudo certbot renew --dry-run

# Auto-renewal is already set up via systemd timer
sudo systemctl status certbot.timer
```

**Your Nginx config will be automatically updated with SSL!**

---

## ⚙️ Systemd Services

### Create Gunicorn Service

```bash
# Create systemd service file
sudo nano /etc/systemd/system/gunicorn.service
```

**Add this configuration**:

```ini
[Unit]
Description=Gunicorn daemon for AGames Django Application
After=network.target postgresql.service redis-server.service

[Service]
Type=notify
User=agames
Group=www-data
WorkingDirectory=/var/www/agames
Environment="PATH=/var/www/agames/venv/bin"
EnvironmentFile=/var/www/agames/.env
ExecStart=/var/www/agames/venv/bin/gunicorn \
    --config /var/www/agames/gunicorn_config.py \
    gamezone.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
# Reload systemd
sudo systemctl daemon-reload

# Start Gunicorn
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
sudo systemctl status gunicorn

# View logs
sudo journalctl -u gunicorn -f
```

### Verify Everything Works

```bash
# Check all services
sudo systemctl status nginx
sudo systemctl status gunicorn
sudo systemctl status postgresql
sudo systemctl status redis-server

# Test the application
curl http://localhost:8000/api/
curl http://YOUR_DOMAIN.com/api/
```

---

## 📊 Monitoring & Maintenance

### System Monitoring Commands

```bash
# Check memory usage
free -h
htop

# Check disk usage
df -h
ncdu /var/www/agames

# Check service logs
sudo journalctl -u gunicorn -f
sudo journalctl -u nginx -f
sudo tail -f /var/log/postgresql/postgresql-14-main.log
sudo tail -f /var/log/redis/redis-server.log

# Check active connections
ss -tuln | grep :80
ss -tuln | grep :443
ss -tuln | grep :8000

# Monitor PostgreSQL
sudo -u postgres psql agames_db -c "SELECT * FROM pg_stat_activity;"

# Monitor Redis
redis-cli INFO stats
redis-cli DBSIZE
```

### Regular Maintenance Tasks

```bash
# Update system (weekly)
sudo apt update && sudo apt upgrade -y

# Restart services (after updates)
sudo systemctl restart gunicorn
sudo systemctl restart nginx

# Clean old logs (monthly)
sudo journalctl --vacuum-time=30d

# Backup database (daily - set up cron job)
sudo -u postgres pg_dump agames_db > /var/backups/agames_db_$(date +%Y%m%d).sql

# Check SSL certificate expiry
sudo certbot certificates
```

### Setup Automated Backups

```bash
# Create backup script
sudo nano /usr/local/bin/backup-agames.sh
```

**Add**:
```bash
#!/bin/bash
BACKUP_DIR="/var/backups/agames"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
sudo -u postgres pg_dump agames_db | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup media files
tar -czf $BACKUP_DIR/media_$DATE.tar.gz -C /var/www/agames media

# Keep only last 7 days
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup completed: $DATE"
```

```bash
# Make executable
sudo chmod +x /usr/local/bin/backup-agames.sh

# Add to cron (daily at 2 AM)
sudo crontab -e
# Add line:
0 2 * * * /usr/local/bin/backup-agames.sh >> /var/log/agames-backup.log 2>&1
```

---

## 🐛 Troubleshooting

### Issue: Gunicorn won't start

```bash
# Check logs
sudo journalctl -u gunicorn -n 50

# Common fixes:
# 1. Check .env file exists
ls -la /var/www/agames/.env

# 2. Check permissions
sudo chown agames:www-data /var/www/agames -R

# 3. Test manually
cd /var/www/agames
source venv/bin/activate
gunicorn --config gunicorn_config.py gamezone.wsgi:application
```

### Issue: 502 Bad Gateway

```bash
# Check Gunicorn is running
sudo systemctl status gunicorn

# Check Nginx config
sudo nginx -t

# Check Gunicorn socket
ss -tuln | grep 8000

# Restart both
sudo systemctl restart gunicorn nginx
```

### Issue: Database connection errors

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check database exists
sudo -u postgres psql -l | grep agames

# Test connection
psql -h localhost -U agames_user -d agames_db

# Check .env DATABASE_URL
cat /var/www/agames/.env | grep DATABASE_URL
```

### Issue: Static files not loading

```bash
# Recollect static files
cd /var/www/agames
source venv/bin/activate
python manage.py collectstatic --noinput

# Check permissions
ls -la staticfiles/
sudo chown -R agames:www-data staticfiles/
sudo chmod -R 755 staticfiles/
```

### Issue: High memory usage

```bash
# Check memory
free -h
htop

# Reduce workers if needed
sudo nano /var/www/agames/.env
# Set: GUNICORN_WORKERS=5
sudo systemctl restart gunicorn

# Clear Redis cache
redis-cli FLUSHDB
```

---

## 🎯 Performance Optimization Tips

1. **Enable PostgreSQL Query Logging** (for slow queries):
   ```sql
   ALTER DATABASE agames_db SET log_min_duration_statement = 1000;
   ```

2. **Monitor Gunicorn workers**:
   ```bash
   ps aux | grep gunicorn
   ```

3. **Use Django Debug Toolbar** (development only):
   ```bash
   pip install django-debug-toolbar
   ```

4. **Enable Nginx caching** (add to nginx config):
   ```nginx
   proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m max_size=100m;
   ```

5. **Monitor with htop**:
   ```bash
   htop
   # Press F5 for tree view
   # Press F6 to sort by CPU/Memory
   ```

---

## 📝 Final Checklist

- [ ] Server purchased and accessible via SSH
- [ ] Firewall configured (ports 80, 443, 22)
- [ ] PostgreSQL installed and optimized
- [ ] Redis installed and configured
- [ ] Application code deployed to `/var/www/agames`
- [ ] Virtual environment created and dependencies installed
- [ ] `.env` file configured with all secrets
- [ ] Database migrated and superuser created
- [ ] Static files collected
- [ ] Nginx configured and running
- [ ] SSL certificate installed
- [ ] Gunicorn service running
- [ ] All services set to start on boot
- [ ] Backups configured
- [ ] Monitoring tools installed

---

## 🎉 Success!

Your AGames backend is now deployed on Hetzner CPX22!

**Access your application**:
- **API**: https://yourdomain.com/api/
- **Admin Panel**: https://yourdomain.com/admin/
- **API Docs**: https://yourdomain.com/api/schema/swagger-ui/

**Next Steps**:
1. Configure your domain's DNS to point to server IP
2. Test all API endpoints
3. Set up monitoring alerts
4. Create deployment scripts for updates

---

## 📞 Support

For issues:
1. Check logs: `sudo journalctl -u gunicorn -f`
2. Review this guide
3. Check Django documentation
4. Contact Hetzner support for server issues

**Estimated deployment time**: 1-2 hours for first-time setup

Good luck! 🚀
