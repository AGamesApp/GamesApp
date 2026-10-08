# 🚀 HETZNER DEPLOYMENT GUIDE - GameZone Project

## 🎯 Recommended Hetzner Server (200 Concurrent Users)

### **Option 1: Best Value - Hetzner Cloud CX31** ⭐
```yaml
vCPU: 2 AMD EPYC (Dedicated)
RAM: 8 GB
Storage: 80 GB NVMe SSD
Traffic: 20 TB/month
Network: 20 Gbit/s
Price: €8.21/month (~$9 USD)
```
**Perfect for starting - can handle 200+ concurrent users easily!**

### **Option 2: Better Performance - Hetzner Cloud CPX31**
```yaml
vCPU: 4 AMD EPYC (Shared)
RAM: 8 GB
Storage: 160 GB NVMe SSD
Traffic: 20 TB/month
Network: 20 Gbit/s
Price: €13.90/month (~$15 USD)
```

### **Option 3: Maximum Performance - Hetzner Cloud CCX23**
```yaml
vCPU: 8 AMD EPYC (Dedicated)
RAM: 16 GB
Storage: 240 GB NVMe SSD
Traffic: 20 TB/month
Network: 20 Gbit/s
Price: €28.21/month (~$31 USD)
```

## 💰 Total Monthly Cost Breakdown

### Budget Setup (Recommended to Start)
```
- CX31 Server: €8.21/month
- Volume Backup: €1.19/month (40GB backup)
- Floating IP: €1.19/month (optional)
- Firewall: Free
- Load Balancer: Not needed yet

Total: ~€10.59/month (~$12 USD/month)
```

### Additional Services (All on Same Server)
```
- PostgreSQL: Self-hosted (Free)
- Redis: Self-hosted (Free)
- Nginx: Self-hosted (Free)
- SSL: Let's Encrypt (Free)
- Cloudflare CDN: Free tier
- Backups: Hetzner Snapshots (€0.012/GB/month)

No need for separate database servers!
```

## 🛠️ Complete Deployment Steps

### STEP 1: Create Hetzner Cloud Server

```bash
# Go to: https://console.hetzner.cloud/
# 1. Create new project: "GameZone"
# 2. Add Server:
#    - Location: Nuremberg or Helsinki (EU) or Ashburn (US)
#    - Image: Ubuntu 22.04
#    - Type: CX31 (Recommended)
#    - Networking: IPv4 + IPv6
#    - SSH Key: Add your public key
#    - Firewall: Create new
#      - Allow: 22 (SSH), 80 (HTTP), 443 (HTTPS)
#      - Block: Everything else
#    - Backups: Enable automatic backups (€1.19/month)
#    - Name: gamezone-prod
```

### STEP 2: Initial Server Setup

```bash
# SSH into server (use IP from Hetzner console)
ssh root@YOUR_SERVER_IP

# Update system
apt update && apt upgrade -y

# Set timezone
timedatectl set-timezone UTC

# Create deploy user
adduser deploy
usermod -aG sudo deploy

# Setup SSH for deploy user
mkdir -p /home/deploy/.ssh
cp /root/.ssh/authorized_keys /home/deploy/.ssh/
chown -R deploy:deploy /home/deploy/.ssh
chmod 700 /home/deploy/.ssh
chmod 600 /home/deploy/.ssh/authorized_keys

# Disable root login (security)
sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
systemctl restart sshd

# Setup firewall with UFW
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# Exit and login as deploy user
exit
ssh deploy@YOUR_SERVER_IP
```

### STEP 3: Install Required Software

```bash
# System packages
sudo apt install -y python3.11 python3.11-venv python3-pip \
    nginx postgresql postgresql-contrib redis-server \
    git curl wget htop supervisor certbot python3-certbot-nginx \
    build-essential libpq-dev python3-dev

# Verify installations
python3.11 --version
psql --version
redis-cli --version
nginx -v
```

### STEP 4: Setup PostgreSQL

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE gamezone_db;
CREATE USER gamezone_user WITH PASSWORD 'YOUR_SECURE_PASSWORD_HERE';
ALTER ROLE gamezone_user SET client_encoding TO 'utf8';
ALTER ROLE gamezone_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE gamezone_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE gamezone_db TO gamezone_user;
\q

# Optimize PostgreSQL for 8GB RAM
sudo nano /etc/postgresql/14/main/postgresql.conf

# Add these settings:
shared_buffers = 2GB
effective_cache_size = 6GB
maintenance_work_mem = 512MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 10MB
min_wal_size = 1GB
max_wal_size = 4GB
max_connections = 200

# Restart PostgreSQL
sudo systemctl restart postgresql
sudo systemctl enable postgresql
```

### STEP 5: Setup Redis

```bash
# Configure Redis
sudo nano /etc/redis/redis.conf

# Modify these lines:
maxmemory 1gb
maxmemory-policy allkeys-lru
bind 127.0.0.1
supervised systemd

# Restart Redis
sudo systemctl restart redis-server
sudo systemctl enable redis-server

# Test Redis
redis-cli ping  # Should return PONG
```

### STEP 6: Deploy Django Application

```bash
# Create project directory
sudo mkdir -p /var/www/gamezone
sudo chown deploy:deploy /var/www/gamezone
cd /var/www/gamezone

# Clone your repository
git clone https://github.com/YOUR_USERNAME/game.git .
# OR upload your files via SCP/SFTP

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

# Create .env file
nano .env
```

**Copy this .env template:**
```env
# Django Settings
SECRET_KEY=GENERATE_NEW_SECRET_KEY_HERE_50_CHARACTERS
DEBUG=False
ALLOWED_HOSTS=YOUR_DOMAIN.COM,www.YOUR_DOMAIN.COM,YOUR_SERVER_IP

# Database
DB_NAME=gamezone_db
DB_USER=gamezone_user
DB_PASSWORD=YOUR_SECURE_PASSWORD_HERE
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://127.0.0.1:6379/1

# Firebase (for push notifications)
FIREBASE_CREDENTIALS_PATH=/var/www/gamezone/firebase-credentials.json

# Stripe (for payments)
STRIPE_PUBLIC_KEY=pk_live_xxxxx
STRIPE_SECRET_KEY=sk_live_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx

# Email (optional)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

```bash
# Generate SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Update settings.py to use .env
# (Your settings already has this configured)

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Create required directories
mkdir -p /var/www/gamezone/media/game_images
mkdir -p /var/www/gamezone/media/emulator_icons
mkdir -p /var/log/gamezone
sudo chown -R deploy:www-data /var/www/gamezone
sudo chmod -R 755 /var/www/gamezone
```

### STEP 7: Setup Gunicorn

```bash
# Create Gunicorn config
nano /var/www/gamezone/gunicorn_config.py
```

```python
# Gunicorn configuration
import multiprocessing

# Server socket
bind = "unix:/var/www/gamezone/gamezone.sock"
backlog = 2048

# Worker processes
workers = 5  # (2 x CPU cores) + 1 = (2 x 2) + 1 = 5
worker_class = "sync"
worker_connections = 1000
threads = 2
timeout = 120
keepalive = 5

# Request handling
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "/var/log/gamezone/gunicorn-access.log"
errorlog = "/var/log/gamezone/gunicorn-error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "gamezone"

# Server mechanics
daemon = False
pidfile = "/var/run/gamezone.pid"
user = "deploy"
group = "www-data"
umask = 0o007
```

```bash
# Create systemd service
sudo nano /etc/systemd/system/gamezone.service
```

```ini
[Unit]
Description=GameZone Gunicorn Service
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=deploy
Group=www-data
RuntimeDirectory=gunicorn
WorkingDirectory=/var/www/gamezone
Environment="PATH=/var/www/gamezone/venv/bin"
EnvironmentFile=/var/www/gamezone/.env
ExecStart=/var/www/gamezone/venv/bin/gunicorn \
          --config /var/www/gamezone/gunicorn_config.py \
          gamezone.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

```bash
# Start and enable Gunicorn
sudo systemctl daemon-reload
sudo systemctl start gamezone
sudo systemctl enable gamezone
sudo systemctl status gamezone
```

### STEP 8: Setup Nginx

```bash
# Create Nginx config
sudo nano /etc/nginx/sites-available/gamezone
```

```nginx
# Rate limiting zones
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=5r/s;
limit_conn_zone $binary_remote_addr zone=addr:10m;

# Upstream Gunicorn
upstream gamezone_app {
    server unix:/var/www/gamezone/gamezone.sock fail_timeout=0;
}

# Redirect HTTP to HTTPS (will be enabled after SSL)
server {
    listen 80;
    listen [::]:80;
    server_name YOUR_DOMAIN.COM www.YOUR_DOMAIN.COM;
    
    # Temporarily allow traffic for Let's Encrypt
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    # Comment this out initially, uncomment after getting SSL
    # return 301 https://$server_name$request_uri;
    
    # Temporary - remove after SSL is working
    location / {
        proxy_pass http://gamezone_app;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
    
    location /static/ {
        alias /var/www/gamezone/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /var/www/gamezone/media/;
        expires 7d;
        add_header Cache-Control "public";
    }
}

# HTTPS server (uncomment after getting SSL certificate)
# server {
#     listen 443 ssl http2;
#     listen [::]:443 ssl http2;
#     server_name YOUR_DOMAIN.COM www.YOUR_DOMAIN.COM;
#
#     # SSL Configuration (Let's Encrypt will add this)
#     ssl_certificate /etc/letsencrypt/live/YOUR_DOMAIN.COM/fullchain.pem;
#     ssl_certificate_key /etc/letsencrypt/live/YOUR_DOMAIN.COM/privkey.pem;
#     ssl_protocols TLSv1.2 TLSv1.3;
#     ssl_ciphers HIGH:!aNULL:!MD5;
#     ssl_prefer_server_ciphers on;
#     ssl_session_cache shared:SSL:10m;
#     ssl_session_timeout 10m;
#
#     # Security Headers
#     add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
#     add_header X-Frame-Options "DENY" always;
#     add_header X-Content-Type-Options "nosniff" always;
#     add_header X-XSS-Protection "1; mode=block" always;
#
#     # Client settings
#     client_max_body_size 500M;
#     client_body_buffer_size 128k;
#     
#     # Rate limiting
#     limit_req zone=api_limit burst=20 nodelay;
#     limit_conn addr 10;
#
#     # Static files
#     location /static/ {
#         alias /var/www/gamezone/staticfiles/;
#         expires 30d;
#         add_header Cache-Control "public, immutable";
#         access_log off;
#     }
#
#     # Media files
#     location /media/ {
#         alias /var/www/gamezone/media/;
#         expires 7d;
#         add_header Cache-Control "public";
#     }
#
#     # Authentication endpoints (stricter rate limit)
#     location ~ ^/api/users/(login|register) {
#         limit_req zone=auth_limit burst=5 nodelay;
#         proxy_pass http://gamezone_app;
#         proxy_set_header Host $http_host;
#         proxy_set_header X-Real-IP $remote_addr;
#         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
#         proxy_set_header X-Forwarded-Proto $scheme;
#         proxy_redirect off;
#     }
#
#     # Main application
#     location / {
#         proxy_pass http://gamezone_app;
#         proxy_set_header Host $http_host;
#         proxy_set_header X-Real-IP $remote_addr;
#         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
#         proxy_set_header X-Forwarded-Proto $scheme;
#         proxy_redirect off;
#         proxy_buffering off;
#         
#         # Timeouts
#         proxy_connect_timeout 120s;
#         proxy_send_timeout 120s;
#         proxy_read_timeout 120s;
#     }
# }
```

```bash
# Enable site and test
sudo ln -s /etc/nginx/sites-available/gamezone /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default  # Remove default site
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### STEP 9: Get SSL Certificate (Let's Encrypt)

```bash
# Make sure your domain points to server IP first!
# Check with: dig YOUR_DOMAIN.COM

# Get certificate
sudo certbot --nginx -d YOUR_DOMAIN.COM -d www.YOUR_DOMAIN.COM

# Follow the prompts:
# - Enter email
# - Agree to terms
# - Choose option 2: Redirect HTTP to HTTPS

# Test auto-renewal
sudo certbot renew --dry-run

# Certificate will auto-renew via cron
```

### STEP 10: Setup Automated Backups

```bash
# Create backup script
sudo nano /usr/local/bin/backup_gamezone.sh
```

```bash
#!/bin/bash
# GameZone Backup Script

BACKUP_DIR="/var/backups/gamezone"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup PostgreSQL database
echo "Backing up database..."
sudo -u postgres pg_dump gamezone_db | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup media files
echo "Backing up media files..."
tar -czf $BACKUP_DIR/media_$DATE.tar.gz -C /var/www/gamezone media/

# Backup .env and configs
echo "Backing up configuration..."
tar -czf $BACKUP_DIR/config_$DATE.tar.gz \
    /var/www/gamezone/.env \
    /etc/nginx/sites-available/gamezone \
    /etc/systemd/system/gamezone.service

# Remove old backups
echo "Cleaning old backups..."
find $BACKUP_DIR -type f -mtime +$RETENTION_DAYS -delete

# Calculate backup size
BACKUP_SIZE=$(du -sh $BACKUP_DIR | cut -f1)
echo "Backup complete! Total size: $BACKUP_SIZE"

# Optional: Upload to Hetzner Storage Box or S3
# rclone copy $BACKUP_DIR remote:gamezone-backups/
```

```bash
# Make executable
sudo chmod +x /usr/local/bin/backup_gamezone.sh

# Add to crontab (daily at 2 AM)
sudo crontab -e
# Add this line:
0 2 * * * /usr/local/bin/backup_gamezone.sh >> /var/log/gamezone/backup.log 2>&1

# Test backup
sudo /usr/local/bin/backup_gamezone.sh
```

### STEP 11: Setup Monitoring

```bash
# Install monitoring tools
sudo apt install -y htop iotop nethogs

# Setup logrotate for Django logs
sudo nano /etc/logrotate.d/gamezone
```

```
/var/log/gamezone/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 deploy www-data
    sharedscripts
    postrotate
        systemctl reload gamezone
    endscript
}
```

```bash
# Create health check endpoint monitoring
# Add to crontab
crontab -e
# Add this line to check if site is up every 5 minutes:
*/5 * * * * curl -f http://YOUR_DOMAIN.COM/api/health/ || systemctl restart gamezone
```

## 🔧 Hetzner-Specific Optimizations

### Enable BBR TCP Congestion Control (Better Performance)
```bash
# BBR improves network throughput
sudo nano /etc/sysctl.conf

# Add these lines:
net.core.default_qdisc=fq
net.ipv4.tcp_congestion_control=bbr

# Apply changes
sudo sysctl -p
```

### Use Hetzner Cloud Volumes (Optional - for large media)
```bash
# If you need more storage for game files/media
# Create volume in Hetzner console, then:

# Attach and mount volume
sudo mkfs.ext4 /dev/disk/by-id/scsi-0HC_Volume_XXXXX
sudo mkdir -p /mnt/gamezone-media
sudo mount -o discard,defaults /dev/disk/by-id/scsi-0HC_Volume_XXXXX /mnt/gamezone-media

# Add to fstab for auto-mount
echo '/dev/disk/by-id/scsi-0HC_Volume_XXXXX /mnt/gamezone-media ext4 discard,nofail,defaults 0 0' | sudo tee -a /etc/fstab

# Move media to volume
sudo mv /var/www/gamezone/media/* /mnt/gamezone-media/
sudo ln -s /mnt/gamezone-media /var/www/gamezone/media
```

### Setup Hetzner Snapshots (Better than backups)
```bash
# In Hetzner Cloud Console:
# 1. Go to your server
# 2. Click "Snapshots"
# 3. Create snapshot (€0.012/GB/month when server is off)
# 4. Schedule weekly snapshots via API or manually

# Alternatively use Hetzner's automated backups
# (Already enabled if you selected it during creation)
```

## 🌍 Cloudflare CDN Integration (Free)

```bash
# 1. Add your domain to Cloudflare (free account)
# 2. Update nameservers at your domain registrar
# 3. In Cloudflare dashboard:
#    - SSL/TLS → Full (strict)
#    - Speed → Optimization → Auto Minify (CSS, JS, HTML)
#    - Caching → Browser Cache TTL → 1 month
#    - Firewall → Add rules to block bad bots
# 4. Update Nginx to allow Cloudflare IPs only (optional security)
```

## 📊 Performance Testing

```bash
# Install testing tools
sudo apt install -y apache2-utils

# Test response time
curl -w "@-" -o /dev/null -s http://YOUR_DOMAIN.COM <<'EOF'
    time_namelookup:  %{time_namelookup}\n
       time_connect:  %{time_connect}\n
    time_appconnect:  %{time_appconnect}\n
   time_pretransfer:  %{time_pretransfer}\n
      time_redirect:  %{time_redirect}\n
 time_starttransfer:  %{time_starttransfer}\n
                    ----------\n
         time_total:  %{time_total}\n
EOF

# Load testing (100 requests, 10 concurrent)
ab -n 100 -c 10 http://YOUR_DOMAIN.COM/api/games/

# More realistic load test (1000 requests, 50 concurrent)
ab -n 1000 -c 50 -t 30 http://YOUR_DOMAIN.COM/api/games/
```

## 🔐 Security Hardening

```bash
# Install fail2ban (block brute force attacks)
sudo apt install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Configure fail2ban for Nginx
sudo nano /etc/fail2ban/jail.local
```

```ini
[nginx-http-auth]
enabled = true

[nginx-noscript]
enabled = true

[nginx-badbots]
enabled = true

[nginx-noproxy]
enabled = true
```

```bash
# Restart fail2ban
sudo systemctl restart fail2ban

# Auto security updates
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

## 🚀 Deploy Updates

```bash
# Create deployment script
nano /var/www/gamezone/deploy.sh
```

```bash
#!/bin/bash
# Quick deployment script

cd /var/www/gamezone
source venv/bin/activate

# Pull latest code
git pull origin main

# Install/update dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart services
sudo systemctl restart gamezone
sudo systemctl reload nginx

echo "✅ Deployment complete!"
```

```bash
chmod +x /var/www/gamezone/deploy.sh

# To deploy updates:
/var/www/gamezone/deploy.sh
```

## 📋 Post-Deployment Checklist

- [ ] Server created on Hetzner
- [ ] Firewall configured (22, 80, 443)
- [ ] PostgreSQL installed and configured
- [ ] Redis installed and configured
- [ ] Django application deployed
- [ ] Gunicorn service running
- [ ] Nginx configured and running
- [ ] SSL certificate obtained
- [ ] Domain DNS pointing to server
- [ ] HTTPS working
- [ ] Static files serving correctly
- [ ] Media files uploading correctly
- [ ] Database migrations completed
- [ ] Superuser created
- [ ] Automated backups configured
- [ ] Monitoring setup
- [ ] Cloudflare CDN configured (optional)
- [ ] Load testing passed
- [ ] API endpoints working

## 🆘 Troubleshooting

### Server not responding
```bash
# Check Gunicorn
sudo systemctl status gamezone
sudo journalctl -u gamezone -n 50

# Check Nginx
sudo systemctl status nginx
sudo nginx -t
sudo tail -f /var/log/nginx/error.log

# Check firewall
sudo ufw status
```

### Database issues
```bash
# Check PostgreSQL
sudo systemctl status postgresql
sudo -u postgres psql -c "\l"  # List databases
sudo -u postgres psql -c "\du"  # List users
```

### High load
```bash
# Check system resources
htop
iotop
nethogs

# Check slow queries
sudo -u postgres psql gamezone_db -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"
```

## 💡 Cost Optimization Tips

1. **Start with CX31** (€8.21/month) - Handles 200+ users easily
2. **Use Hetzner's automated backups** instead of snapshots if on budget
3. **Cloudflare free tier** for CDN (saves massive bandwidth)
4. **Self-host everything** on one server initially
5. **Scale vertically** first (upgrade server size) before horizontal scaling
6. **Use Hetzner Storage Box** (€3.81/month for 100GB) for backups instead of volumes

## 📞 Support

- Hetzner Docs: https://docs.hetzner.com/
- Hetzner Status: https://status.hetzner.com/
- Support Ticket: https://console.hetzner.cloud/ (fast response!)

---

**Total Setup Time**: 1-2 hours
**Monthly Cost**: €10-30 depending on server choice
**Performance**: Can handle 200-500+ concurrent users
**Uptime**: 99.9%+ guaranteed by Hetzner

🎉 Your GameZone project is ready for production on Hetzner!
