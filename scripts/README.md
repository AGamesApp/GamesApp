# AGames Deployment Scripts

This directory contains automation scripts for deploying AGames on Hetzner CPX22.

## 📁 Scripts Overview

### 1. `setup_server.sh` - Initial Server Setup
**Purpose**: Automates the initial server configuration and dependency installation.

**What it does**:
- Updates system packages
- Installs Python 3.11, PostgreSQL, Redis, Nginx
- Configures firewall (UFW)
- Creates application user (`agames`)
- Sets up PostgreSQL database
- Optimizes PostgreSQL for CPX22 (4GB RAM)
- Configures Redis with memory limits
- Installs Certbot for SSL

**Usage**:
```bash
# Run as root on fresh server
ssh root@YOUR_SERVER_IP
wget YOUR_REPO_URL/scripts/setup_server.sh
bash setup_server.sh
```

**Time**: ~5-10 minutes

---

### 2. `deploy.sh` - Application Deployment
**Purpose**: Deploys the Django application and configures all services.

**What it does**:
- Creates Python virtual environment
- Installs Python dependencies
- Creates/validates `.env` file
- Runs database migrations
- Collects static files
- Creates media directories
- Sets up Gunicorn systemd service
- Configures Nginx
- Optionally installs SSL certificate

**Usage**:
```bash
# Run as agames user after setup_server.sh
su - agames
cd /var/www/agames
bash scripts/deploy.sh
```

**Prerequisites**:
- Server setup completed (`setup_server.sh`)
- Repository cloned to `/var/www/agames`

**Time**: ~5-10 minutes

---

### 3. `update.sh` - Zero-Downtime Updates
**Purpose**: Updates the application with zero downtime.

**What it does**:
- Creates backup (database + media)
- Pulls latest code from git
- Updates Python dependencies
- Runs database migrations
- Collects static files
- Reloads Gunicorn (zero downtime)
- Optionally runs tests
- Optionally clears Redis cache
- Cleans up old backups (>7 days)

**Usage**:
```bash
# Run as agames user for updates
cd /var/www/agames
bash scripts/update.sh
```

**Features**:
- Zero downtime (uses `systemctl reload`)
- Automatic rollback on failure
- Backup before update
- Optional testing before deployment

**Time**: ~2-5 minutes

---

## 🚀 Quick Start

### First-Time Deployment:

```bash
# 1. On your Hetzner server (as root)
ssh root@YOUR_SERVER_IP
wget YOUR_REPO/scripts/setup_server.sh
bash setup_server.sh

# 2. Switch to app user
su - agames

# 3. Clone repository
cd /var/www/agames
git clone YOUR_REPO_URL .

# 4. Deploy application
bash scripts/deploy.sh

# 5. Install SSL (optional)
sudo certbot --nginx -d yourdomain.com
```

### Updates:

```bash
# On your server (as agames user)
ssh agames@YOUR_SERVER_IP
cd /var/www/agames
bash scripts/update.sh
```

---

## 📝 Prerequisites

### For `setup_server.sh`:
- Fresh Ubuntu 22.04 server (Hetzner CPX22)
- Root access
- Internet connection

### For `deploy.sh`:
- `setup_server.sh` completed
- Repository cloned to `/var/www/agames`
- Running as `agames` user

### For `update.sh`:
- Application already deployed
- Git repository initialized
- Running as `agames` user

---

## ⚙️ Configuration

All scripts use these default values:

| Variable | Default Value | Description |
|----------|--------------|-------------|
| APP_USER | agames | Application user |
| APP_DIR | /var/www/agames | Application directory |
| PYTHON_VERSION | python3.11 | Python version |
| DB_NAME | agames_db | PostgreSQL database |
| DB_USER | agames_user | PostgreSQL user |
| BACKUP_DIR | /var/backups/agames | Backup directory |

You can modify these in the scripts if needed.

---

## 🔍 What Each Script Installs/Configures

### `setup_server.sh` installs:
- ✅ Python 3.11 + pip + venv
- ✅ Build tools (gcc, make, etc.)
- ✅ PostgreSQL 14
- ✅ Redis 7.x
- ✅ Nginx
- ✅ Certbot (Let's Encrypt)
- ✅ System utilities (htop, ncdu, iotop)

### `deploy.sh` sets up:
- ✅ Python virtual environment
- ✅ Django dependencies
- ✅ Database schema
- ✅ Static files collection
- ✅ Media directories
- ✅ Gunicorn systemd service
- ✅ Nginx site configuration
- ✅ SSL certificate (optional)

### `update.sh` performs:
- ✅ Database backup
- ✅ Media backup
- ✅ Git pull
- ✅ Dependencies update
- ✅ Migrations
- ✅ Static files update
- ✅ Zero-downtime reload

---

## 🛠️ Customization

### Modify Worker Count:

Edit `.env` file:
```env
GUNICORN_WORKERS=7  # Default for CPX22 (3 vCPU)
```

For different server sizes:
- **CPX11** (2 vCPU, 2GB RAM): `GUNICORN_WORKERS=5`
- **CPX22** (3 vCPU, 4GB RAM): `GUNICORN_WORKERS=7` ← Current
- **CPX32** (4 vCPU, 8GB RAM): `GUNICORN_WORKERS=9`
- **CPX42** (8 vCPU, 16GB RAM): `GUNICORN_WORKERS=17`

### Add Custom Setup Steps:

Edit scripts and add before the final summary:

```bash
# In setup_server.sh, before print_status "Server setup completed"
print_status "Installing custom tools..."
apt install -y your-custom-package
```

---

## 🐛 Troubleshooting

### Script fails with "Permission denied":

```bash
# Make scripts executable
chmod +x scripts/*.sh
```

### Script fails during database setup:

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Manually create database
sudo -u postgres psql
CREATE DATABASE agames_db;
CREATE USER agames_user WITH PASSWORD 'your-password';
GRANT ALL PRIVILEGES ON DATABASE agames_db TO agames_user;
\q
```

### Gunicorn fails to start:

```bash
# Check logs
sudo journalctl -u gunicorn -n 50

# Common issues:
# 1. .env file missing/incorrect
# 2. Database connection failed
# 3. Python dependencies not installed

# Test manually
cd /var/www/agames
source venv/bin/activate
python manage.py check
gunicorn --config gunicorn_config.py gamezone.wsgi:application
```

### Nginx returns 502 Bad Gateway:

```bash
# Check Gunicorn is running
sudo systemctl status gunicorn

# Check Gunicorn is listening on port 8000
ss -tuln | grep 8000

# Restart services
sudo systemctl restart gunicorn nginx
```

---

## 📊 Success Indicators

After running scripts, you should see:

### After `setup_server.sh`:
```
✅ PostgreSQL: Active and running
✅ Redis: Active and running
✅ Nginx: Active and running
✅ Firewall: Active (ports 22, 80, 443)
✅ User 'agames' created
✅ Directory /var/www/agames created
```

### After `deploy.sh`:
```
✅ Virtual environment created
✅ Dependencies installed
✅ Database migrated
✅ Static files collected
✅ Gunicorn service running
✅ Nginx serving application
✅ SSL certificate installed (if enabled)
```

### After `update.sh`:
```
✅ Backup created
✅ Code updated
✅ Dependencies updated
✅ Migrations applied
✅ Gunicorn reloaded (zero downtime)
✅ Services still running
```

---

## 📝 Logs Location

### Script execution logs:
```bash
# View last setup
cat /var/log/agames-setup.log

# View last backup
cat /var/log/agames-backup.log
```

### Service logs:
```bash
# Gunicorn
sudo journalctl -u gunicorn -f

# Nginx
sudo tail -f /var/log/nginx/error.log

# PostgreSQL
sudo tail -f /var/log/postgresql/postgresql-14-main.log

# Redis
sudo tail -f /var/log/redis/redis-server.log
```

---

## 🔐 Security Notes

1. **Never commit .env file** - Contains sensitive credentials
2. **Use SSH keys** - More secure than passwords
3. **Enable firewall** - Scripts configure UFW automatically
4. **Set strong passwords** - For database and Redis
5. **Install SSL** - Always use HTTPS in production
6. **Regular updates** - Run `update.sh` frequently
7. **Monitor logs** - Check for suspicious activity

---

## 📚 Additional Resources

- **Full Deployment Guide**: [CPX22_DEPLOYMENT_GUIDE.md](../CPX22_DEPLOYMENT_GUIDE.md)
- **Quick Reference**: [DEPLOYMENT_SUMMARY.md](../DEPLOYMENT_SUMMARY.md)
- **Configuration Files**: [configs/](../configs/)

---

## 💡 Tips

1. **Test in development first** - Use a test server before production
2. **Keep backups** - Scripts backup automatically, but also backup manually
3. **Monitor resources** - Use `htop` to check CPU/RAM usage
4. **Use git tags** - Tag releases for easy rollback
5. **Schedule updates** - Update during low-traffic periods
6. **Read logs** - Check logs after deployment to catch errors early

---

## 🤝 Contributing

To improve these scripts:

1. Test changes on a test server first
2. Document any new features
3. Update this README
4. Follow existing code style
5. Add error handling

---

## 📄 License

These scripts are part of the AGames project.

---

**Need help?** Check the [Troubleshooting](#troubleshooting) section or full deployment guide.

**Ready to deploy?** Start with `setup_server.sh` on your Hetzner CPX22 server!

🚀 Happy deploying!
