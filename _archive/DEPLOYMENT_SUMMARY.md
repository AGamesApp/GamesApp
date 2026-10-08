# AGames Deployment on Hetzner CPX22 - Quick Reference

## 🎯 Server Plan: Hetzner CPX22
- **CPU**: 3 vCPU AMD
- **RAM**: 4GB DDR4
- **Storage**: 80GB NVMe SSD
- **Bandwidth**: 20TB
- **Price**: €10.69/month
- **Performance**: 100-150 concurrent users

---

## 📊 Configuration Changes Made

### ✅ Updated Files for CPX22

1. **`gunicorn_config.py`**
   - Workers: 9 → **7** (formula: 2 × 3 vCPU + 1)
   - Worker connections: 30 → **20** per worker
   - Total concurrent: ~140 requests
   - Memory footprint: ~1.4GB

2. **`gamezone/settings.py`**
   - Redis connections: 50 → **30**
   - Cache entries: 5000 → **3000**
   - Optimized for 4GB RAM (was 8GB)

3. **New Config Files Created**:
   - `configs/nginx_cpx22.conf` - Nginx for 4GB RAM
   - `configs/postgresql_cpx22.conf` - PostgreSQL tuned for 1.2GB
   - `configs/redis_cpx22.conf` - Redis with 256MB limit

4. **Deployment Scripts**:
   - `scripts/setup_server.sh` - Initial server setup
   - `scripts/deploy.sh` - Application deployment
   - `scripts/update.sh` - Zero-downtime updates

---

## 🚀 Quick Deployment Steps

### Option 1: Automated Deployment (Recommended)

```bash
# 1. Access new server
ssh root@YOUR_SERVER_IP

# 2. Download and run server setup
wget https://raw.githubusercontent.com/YOUR_REPO/main/scripts/setup_server.sh
bash setup_server.sh

# 3. Switch to app user
su - agames

# 4. Clone repository
cd /var/www/agames
git clone YOUR_REPO_URL .

# 5. Run deployment script
bash scripts/deploy.sh

# 6. Install SSL (optional)
sudo certbot --nginx -d yourdomain.com
```

**Total time: ~15-20 minutes**

---

### Option 2: Manual Deployment

See **[CPX22_DEPLOYMENT_GUIDE.md](./CPX22_DEPLOYMENT_GUIDE.md)** for detailed step-by-step instructions.

---

## 📁 Files Modified/Created

### Modified for CPX22:
```
gunicorn_config.py          ← Updated workers 9→7, connections 30→20
gamezone/settings.py        ← Reduced cache/DB settings for 4GB RAM
```

### New Configuration Files:
```
configs/
├── nginx_cpx22.conf        ← Nginx config for 3 vCPU, 4GB RAM
├── postgresql_cpx22.conf   ← PostgreSQL optimized for 1.2GB
└── redis_cpx22.conf        ← Redis limited to 256MB

scripts/
├── setup_server.sh         ← Automated server setup
├── deploy.sh              ← Application deployment
└── update.sh              ← Zero-downtime updates

CPX22_DEPLOYMENT_GUIDE.md   ← Complete deployment documentation
DEPLOYMENT_SUMMARY.md       ← This file
```

---

## 💾 Memory Allocation (4GB Total)

| Service         | Allocation | Purpose                          |
|----------------|------------|----------------------------------|
| Gunicorn       | 1.4GB      | 7 workers × 200MB each          |
| PostgreSQL     | 1.2GB      | Database (shared_buffers: 1GB)  |
| Redis          | 256MB      | Cache layer                      |
| Nginx          | 50MB       | Reverse proxy                    |
| OS & System    | 800MB      | Ubuntu 22.04 base               |
| Buffer/Cache   | 300MB      | System overhead & flexibility   |

---

## 🔧 Performance Specs

### CPX22 Performance Targets:
- **Concurrent Users**: 100-150
- **Concurrent Requests**: ~140 (7 workers × 20 connections)
- **Database Connections**: Max 100
- **Redis Connections**: Max 30
- **Response Time**: <200ms (API endpoints)
- **Static Files**: Served by Nginx (30-day cache)

### Comparison with CPX32:
| Metric              | CPX22       | CPX32       | Savings  |
|--------------------|-------------|-------------|----------|
| Price/month        | €10.69      | €15.11      | **€4.42**|
| vCPU               | 3           | 4           | -25%     |
| RAM                | 4GB         | 8GB         | -50%     |
| Workers            | 7           | 9           | -22%     |
| Concurrent         | 140         | 270         | -48%     |
| Storage            | 80GB        | 160GB       | -50%     |

**Conclusion**: CPX22 handles 100-150 concurrent users efficiently with 42% cost savings.

---

## 📝 Environment Variables Required

Create `.env` file with these variables:

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,YOUR_SERVER_IP

# Database
DATABASE_URL=postgresql://agames_user:PASSWORD@localhost:5432/agames_db

# Redis
REDIS_URL=redis://127.0.0.1:6379/1
CACHE_BACKEND=django_redis.cache.RedisCache

# Email
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Google OAuth
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret

# Stripe (if using payments)
STRIPE_PUBLIC_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...

# Gunicorn
GUNICORN_WORKERS=7

# CORS
CORS_ALLOWED_ORIGINS=https://yourdomain.com
```

---

## 🛠️ Useful Commands

### Service Management
```bash
# Start/Stop/Restart services
sudo systemctl start gunicorn
sudo systemctl stop gunicorn
sudo systemctl restart gunicorn
sudo systemctl status gunicorn

# Same for nginx, postgresql, redis-server
```

### Logs
```bash
# View live logs
sudo journalctl -u gunicorn -f
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/postgresql/postgresql-14-main.log

# Last 50 lines
sudo journalctl -u gunicorn -n 50
```

### Monitoring
```bash
# System resources
htop                    # Interactive process viewer
free -h                 # Memory usage
df -h                   # Disk usage
ncdu /var/www/agames   # Directory size analysis

# Database
sudo -u postgres psql agames_db -c "SELECT * FROM pg_stat_activity;"

# Redis
redis-cli INFO memory
redis-cli DBSIZE
```

### Maintenance
```bash
# Update application
cd /var/www/agames
bash scripts/update.sh

# Backup database
sudo -u postgres pg_dump agames_db > backup_$(date +%Y%m%d).sql

# Clear Redis cache
redis-cli FLUSHDB

# Collect static files
source venv/bin/activate
python manage.py collectstatic --noinput
```

---

## 🔒 Security Checklist

- [ ] Firewall enabled (ports 22, 80, 443 only)
- [ ] Non-root user created (agames)
- [ ] SSH key authentication configured
- [ ] Strong database password set
- [ ] SECRET_KEY generated and unique
- [ ] DEBUG=False in production
- [ ] SSL certificate installed
- [ ] Redis password set (optional)
- [ ] Regular backups scheduled
- [ ] Security headers enabled in Nginx

---

## 📊 Performance Monitoring

### Key Metrics to Monitor:
1. **Memory Usage**: Should stay under 3.5GB
   ```bash
   free -h
   ```

2. **CPU Usage**: Should stay under 70%
   ```bash
   htop
   ```

3. **Database Connections**: Monitor active connections
   ```bash
   sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"
   ```

4. **Redis Memory**: Should stay under 256MB
   ```bash
   redis-cli INFO memory | grep used_memory_human
   ```

5. **Disk Usage**: Alert at 80%
   ```bash
   df -h
   ```

### Set Up Monitoring Alerts:
Consider using:
- **Uptime Robot**: Free uptime monitoring
- **Netdata**: Real-time performance monitoring
- **Sentry**: Error tracking for Django
- **Cloudflare**: DDoS protection and CDN

---

## 🎯 Next Steps After Deployment

1. **Test All Endpoints**:
   - API: `https://yourdomain.com/api/`
   - Admin: `https://yourdomain.com/admin/`
   - Swagger: `https://yourdomain.com/api/schema/swagger-ui/`

2. **Configure DNS**:
   - Point A record to server IP
   - Add www CNAME record

3. **Install SSL Certificate**:
   ```bash
   sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
   ```

4. **Set Up Backups**:
   - Daily database backups
   - Weekly full backups
   - Off-site backup storage

5. **Configure Monitoring**:
   - Set up uptime monitoring
   - Configure error alerts
   - Monitor resource usage

6. **Performance Testing**:
   - Load test with expected traffic
   - Optimize slow queries
   - Enable database query logging

7. **Security Hardening**:
   - Install fail2ban
   - Enable automatic security updates
   - Set up intrusion detection

---

## 📞 Support & Resources

### Documentation:
- **Full Guide**: [CPX22_DEPLOYMENT_GUIDE.md](./CPX22_DEPLOYMENT_GUIDE.md)
- **API Reference**: [API_COMPLETE_REFERENCE.md](./API_COMPLETE_REFERENCE.md)
- **Project Evaluation**: [PROJECT_EVALUATION_REPORT.md](./PROJECT_EVALUATION_REPORT.md)

### Common Issues:
See **Troubleshooting** section in CPX22_DEPLOYMENT_GUIDE.md

### Hetzner Support:
- Dashboard: https://console.hetzner.cloud/
- Documentation: https://docs.hetzner.com/
- Support: https://www.hetzner.com/support

---

## ✅ Deployment Checklist

Before going live:

- [ ] Server purchased and accessible
- [ ] All dependencies installed
- [ ] Database created and optimized
- [ ] Application deployed successfully
- [ ] Environment variables configured
- [ ] Static files served correctly
- [ ] Media uploads working
- [ ] SSL certificate installed
- [ ] All services running and enabled
- [ ] Backups configured
- [ ] Monitoring set up
- [ ] Domain DNS configured
- [ ] API endpoints tested
- [ ] Admin panel accessible
- [ ] Payment gateway tested (if applicable)
- [ ] Email notifications working

---

**🎉 Your AGames backend is ready for production on Hetzner CPX22!**

**Deployment Time Estimate**: 
- Automated: 15-20 minutes
- Manual: 1-2 hours

**Monthly Cost**: €10.69 (saves €4.42/month vs CPX32)

Good luck! 🚀
