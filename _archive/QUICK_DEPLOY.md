# 🚀 Quick Deployment Guide - AGames API

**For experienced developers who want to deploy fast**

---

## ⚡ Prerequisites

- Ubuntu 22.04 VPS (4GB RAM, 2 vCPU)
- Domain name pointed to server IP
- SSH access to server

---

## 📦 One-Command Setup (Copy & Paste)

### Step 1: Initial Server Setup
```bash
# Run as root
apt update && apt upgrade -y && \
apt install -y python3-pip python3-dev python3-venv libpq-dev postgresql postgresql-contrib nginx curl git supervisor redis-server && \
adduser agames && \
usermod -aG sudo agames
```

### Step 2: Database Setup
```bash
# Run as postgres user
sudo -u postgres psql -c "CREATE DATABASE agames_db;"
sudo -u postgres psql -c "CREATE USER agames_user WITH PASSWORD 'CHANGE_THIS_PASSWORD';"
sudo -u postgres psql -c "ALTER ROLE agames_user SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE agames_user SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE agames_user SET timezone TO 'UTC';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE agames_db TO agames_user;"
```

### Step 3: Application Setup
```bash
# Switch to agames user
su - agames

# Clone and setup
cd ~ && \
git clone https://github.com/Ramyrashad127/game.git agames-api && \
cd agames-api && \
python3 -m venv venv && \
source venv/bin/activate && \
pip install --upgrade pip && \
pip install -r requirements.txt gunicorn psycopg2-binary && \
mkdir -p logs
```

### Step 4: Environment Configuration
```bash
# Create .env file
cat > .env << 'EOF'
SECRET_KEY=GENERATE_NEW_KEY_HERE
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

DATABASE_URL=postgresql://agames_user:CHANGE_THIS_PASSWORD@localhost:5432/agames_db

EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=agames.app.dev@gmail.com
EMAIL_HOST_PASSWORD=ukunsishtslgxyez
DEFAULT_FROM_EMAIL=agames.app.dev@gmail.com

GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your-google-client-secret

CORS_ALLOW_ALL_ORIGINS=False
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com

REDIS_URL=redis://localhost:6379/0
CACHE_BACKEND=django_redis.cache.RedisCache
EOF

# Generate SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
# Copy output and replace SECRET_KEY in .env
```

### Step 5: Django Setup
```bash
source venv/bin/activate
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py createsuperuser
```

### Step 6: Gunicorn Service
```bash
# Exit agames user (back to root)
exit

# Create socket
cat > /etc/systemd/system/gunicorn.socket << 'EOF'
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
EOF

# Create service
cat > /etc/systemd/system/gunicorn.service << 'EOF'
[Unit]
Description=gunicorn daemon for AGames API
Requires=gunicorn.socket
After=network.target

[Service]
Type=notify
User=agames
Group=www-data
WorkingDirectory=/home/agames/agames-api
Environment="PATH=/home/agames/agames-api/venv/bin"
ExecStart=/home/agames/agames-api/venv/bin/gunicorn \
          --access-logfile /home/agames/agames-api/logs/gunicorn-access.log \
          --error-logfile /home/agames/agames-api/logs/gunicorn-error.log \
          --workers 3 \
          --timeout 120 \
          --bind unix:/run/gunicorn.sock \
          gamezone.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

# Start Gunicorn
systemctl start gunicorn.socket
systemctl enable gunicorn.socket
systemctl daemon-reload
systemctl restart gunicorn
```

### Step 7: Nginx Configuration
```bash
# Create config (replace your-domain.com)
cat > /etc/nginx/sites-available/agames << 'EOF'
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    client_max_body_size 20M;
    
    location /static/ {
        alias /home/agames/agames-api/staticfiles/;
    }
    
    location /media/ {
        alias /home/agames/agames-api/media/;
    }
    
    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}
EOF

# Enable site
ln -s /etc/nginx/sites-available/agames /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx

# Set permissions
chown -R agames:www-data /home/agames/agames-api
chmod -R 755 /home/agames/agames-api
```

### Step 8: SSL Certificate
```bash
apt install certbot python3-certbot-nginx -y
certbot --nginx -d your-domain.com -d www.your-domain.com
```

### Step 9: Firewall
```bash
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw enable
```

---

## ✅ Verify Deployment

```bash
# Check services
systemctl status gunicorn nginx postgresql redis-server

# Test API
curl https://your-domain.com/api/

# View logs
tail -f /home/agames/agames-api/logs/gunicorn-error.log
```

---

## 🔄 Quick Update Command

```bash
cd /home/agames/agames-api && \
git pull && \
source venv/bin/activate && \
pip install -r requirements.txt && \
python manage.py migrate && \
python manage.py collectstatic --noinput && \
sudo systemctl restart gunicorn
```

---

## 📊 Important URLs

- **API**: `https://your-domain.com/api/`
- **Admin**: `https://your-domain.com/admin/`
- **Custom Admin**: `https://your-domain.com/customadmin/`
- **API Docs**: `https://your-domain.com/api/schema/swagger-ui/`

---

## 🔧 Quick Troubleshooting

### 502 Bad Gateway
```bash
sudo systemctl restart gunicorn
tail -f /home/agames/agames-api/logs/gunicorn-error.log
```

### Static Files Not Loading
```bash
cd /home/agames/agames-api
source venv/bin/activate
python manage.py collectstatic --noinput
sudo systemctl restart nginx
```

### Check All Services
```bash
sudo systemctl status gunicorn nginx postgresql redis-server
```

---

## 💾 Automated Backup

```bash
# Create backup script
cat > /home/agames/backup_db.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/agames/backups"
mkdir -p $BACKUP_DIR
pg_dump -U agames_user agames_db | gzip > $BACKUP_DIR/agames_db_$DATE.sql.gz
find $BACKUP_DIR -name "agames_db_*.sql.gz" -mtime +7 -delete
EOF

chmod +x /home/agames/backup_db.sh

# Add to cron (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /home/agames/backup_db.sh") | crontab -
```

---

## 🎯 Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret (generate new) | Random 50 chars |
| `DEBUG` | Debug mode (False for production) | `False` |
| `ALLOWED_HOSTS` | Allowed domains | `your-domain.com` |
| `DATABASE_URL` | PostgreSQL connection | `postgresql://user:pass@localhost/db` |
| `EMAIL_HOST_USER` | Gmail address | `agames.app.dev@gmail.com` |
| `EMAIL_HOST_PASSWORD` | Gmail app password | `ukunsishtslgxyez` |
| `GOOGLE_CLIENT_ID` | OAuth Client ID | Your OAuth ID |
| `GOOGLE_CLIENT_SECRET` | OAuth Secret | Your OAuth Secret |
| `REDIS_URL` | Redis connection | `redis://localhost:6379/0` |

---

## 📞 Post-Deployment

1. Test all API endpoints
2. Verify email sending (OTP, password reset)
3. Test Google OAuth login
4. Upload test images (profile, game covers)
5. Monitor logs for 24 hours
6. Setup monitoring (optional: UptimeRobot, Sentry)

---

## 🎉 Done!

Your AGames API is now live! 🚀

**Full documentation available in**: `DEPLOYMENT_GUIDE.md`

**Need help?** Check `DEPLOYMENT_CHECKLIST.md` for detailed steps.
