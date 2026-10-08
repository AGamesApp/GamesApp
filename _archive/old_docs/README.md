# AGames - Retro Games Platform
**Version:** 1.0  
**Domain:** games.agames.cv  
**Server:** Hetzner VPS (152.53.206.21)  
**Status:** 🟢 Production Ready

---

## Quick Links

- **Application URL:** https://games.agames.cv 🔒
- **Admin Dashboard:** https://games.agames.cv/customadmin/
- **API Documentation:** https://games.agames.cv/api/docs/
- **API Base URL:** https://games.agames.cv/api/
- **Health Check:** https://games.agames.cv/health/

---

## Project Overview

AGames is a comprehensive retro gaming platform providing:
- 🎮 Multi-emulator game library
- 🔐 Google OAuth & Email authentication
- 💎 Premium subscription system
- 📱 Push notifications via FCM
- 💬 Support ticket system
- ⚡ Redis-cached API responses
- 🔍 Advanced search with subsequence matching

---

## Technology Stack

### Backend
- **Framework:** Django 4.2.7 + Django REST Framework
- **Database:** PostgreSQL 17 (agames_db)
- **Cache:** Redis 5.0.1
- **App Server:** Gunicorn (3 workers)
- **Web Server:** Nginx (reverse proxy)
- **Python:** 3.13

### Security
- **SSL/TLS:** Let's Encrypt certificate (auto-renewal enabled)
- **HTTPS:** TLS 1.2/1.3 with HTTP/2
- **Security Headers:** HSTS, X-Frame-Options, CSP, XSS Protection
- **Password Hashing:** Argon2
- **Authentication:** Token-based + OAuth2 (Google)
- **Firewall:** UFW (ports 22, 80, 443)
- **Rate Limiting:** DRF throttling (50/min users, 20/min anon)
- **Secure Cookies:** HTTPS-only session & CSRF cookies

### Features
- **Email:** SMTP via Gmail (agames.app.dev@gmail.com)
- **Payments:** Stripe integration (configured)
- **Push Notifications:** Firebase Cloud Messaging
- **File Storage:** Local (ready for S3/CDN)

---

## Server Specifications

**Hetzner CPX22 VPS:**
- **CPU:** 4 cores AMD EPYC
- **RAM:** 8GB
- **Storage:** 251GB SSD
- **Network:** 20TB traffic
- **Location:** Germany

**Current Utilization:**
- Memory: 24% used (1.9GB / 7.8GB)
- Disk: 1% used (2.5GB / 251GB)
- CPU Load: 0.14 average (very low)

---

## Documentation

### API Documentation
📁 **[docs/api/](./docs/api/)**
- **[API_ENDPOINTS_REFERENCE.md](./docs/api/API_ENDPOINTS_REFERENCE.md)** - Complete API documentation with all endpoints, headers, bodies, and search techniques

### Deployment Documentation
📁 **[docs/deployment/](./docs/deployment/)**
- **[DEPLOYMENT_INFO.md](./docs/deployment/DEPLOYMENT_INFO.md)** - Deployment guide and server setup
- **[SERVER_PERFORMANCE_EVALUATION.md](./docs/deployment/SERVER_PERFORMANCE_EVALUATION.md)** - Performance analysis and optimization recommendations
- **[REDIS_CACHING_IMPLEMENTATION.md](./docs/deployment/REDIS_CACHING_IMPLEMENTATION.md)** - Redis caching setup and performance metrics
- **[DATABASE_BACKUP_SYSTEM.md](./docs/deployment/DATABASE_BACKUP_SYSTEM.md)** - Automated backup system with daily/weekly schedules

### Security Documentation
📁 **[docs/security/](./docs/security/)**
- **[SECURITY_CONFIG.md](./docs/security/SECURITY_CONFIG.md)** - Security configuration details
- **[SECURITY_REPORT.md](./docs/security/SECURITY_REPORT.md)** - Security audit and recommendations
- **[FIREWALL_SECURITY.md](./docs/security/FIREWALL_SECURITY.md)** - UFW firewall configuration

---

## Quick Start

### Access the Application
```bash
# Web Interface
https://games.agames.cv

# Admin Dashboard
https://games.agames.cv/customadmin/
Username: agames
Email: agames.app.dev@gmail.com

# API Docs (Swagger)
https://games.agames.cv/api/docs/
```

### API Example
```bash
# List all games
curl https://games.agames.cv/api/games/

# Search games
curl https://games.agames.cv/api/games/search/?q=mario

# Get emulators
curl https://games.agames.cv/api/emulators/
```

---

## Project Structure

```
/root/game/
├── docs/                          # Documentation
│   ├── api/                       # API documentation
│   ├── deployment/                # Deployment guides
│   └── security/                  # Security docs
├── gamezone/                      # Django project settings
│   ├── settings.py               # Main configuration
│   ├── urls.py                   # URL routing
│   └── wsgi.py                   # WSGI application
├── games/                         # Games & Emulators app
│   ├── models.py                 # Game, Emulator, Genre models
│   ├── views.py                  # API views (cached)
│   ├── serializers.py            # API serializers
│   └── urls.py                   # App URLs
├── users/                         # User authentication
│   ├── models.py                 # Custom user model
│   ├── views.py                  # Auth endpoints
│   └── google_auth.py            # Google OAuth
├── customadmin/                   # Custom admin dashboard
│   ├── views.py                  # Dashboard views
│   ├── forms.py                  # Admin forms
│   └── templates/                # Dashboard templates
├── subscriptions/                 # Premium subscriptions
├── notifications/                 # Push notifications (FCM)
├── support/                       # Support ticket system
├── payments/                      # Stripe payment processing
├── pages/                         # Static pages (CMS)
├── staticfiles/                   # Collected static files
├── .env                          # Environment variables
├── requirements.txt              # Python dependencies
├── manage.py                     # Django management
├── gunicorn_config.py            # Gunicorn configuration
└── README.md                     # This file
```

---

## Key Features

### 1. Advanced Search
- **Subsequence Matching:** "sfii" matches "Street Fighter II"
- **Case Insensitive:** "MARIO" = "mario"
- **Relevance Ranking:** Best matches first
- **Multi-Filter:** Combine search with emulator, genre, premium filters

### 2. Performance Optimization
- **Redis Caching:** 99% faster cached responses (~2ms vs ~280ms)
- **Database Connection Pooling:** Max 30 connections
- **Gunicorn Workers:** 3 workers optimized for 4 CPU cores
- **Cache Hit Rate:** 73% (excellent)

### 3. Security Features
- ✅ Argon2 password hashing (industry-leading)
- ✅ Security headers (XSS, CSRF, Clickjacking protection)
- ✅ UFW firewall (SSH, HTTP, HTTPS only)
- ✅ Rate limiting (prevent abuse)
- ✅ Token-based authentication
- ✅ OAuth2 Google integration
- ✅ Email verification via OTP

### 4. Admin Dashboard
- 🎮 Game management (CRUD operations)
- 🕹️ Emulator management with `open_outside` control
- 📊 Statistics and analytics
- 👥 User management
- 🎫 Support ticket management
- 📢 Notification broadcasting
- 🔧 System settings

---

## Environment Configuration

### Database
```env
DATABASE_URL=postgresql://agames_user:AGames%40pp%232025@localhost:5432/agames_db
```

### Redis Cache
```env
REDIS_URL=redis://127.0.0.1:6379/1
CACHE_BACKEND=django_redis.cache.RedisCache
```

### Security
```env
SECRET_KEY=74z&28n^gi7zo8dcd1s2+%33y)4o##jpv1jo*+*qm#gsr6^ar8
DEBUG=False
```

### OAuth
```env
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your-google-client-secret
```

---

## Service Management

### Gunicorn (App Server)
```bash
# Status
sudo systemctl status gunicorn

# Restart
sudo systemctl restart gunicorn

# Logs
sudo journalctl -u gunicorn -f
```

### Nginx (Web Server)
```bash
# Status
sudo systemctl status nginx

# Restart
sudo systemctl restart nginx

# Test config
sudo nginx -t
```

### PostgreSQL (Database)
```bash
# Status
sudo systemctl status postgresql

# Connect to database
sudo -u postgres psql -d agames_db
```

### Redis (Cache)
```bash
# Status
sudo systemctl status redis-server

# Monitor
redis-cli MONITOR

# Stats
redis-cli INFO stats
```

---

## Database Credentials

**PostgreSQL:**
- **Database:** agames_db
- **User:** agames_user
- **Password:** AGames@pp#2025
- **Host:** localhost
- **Port:** 5432
- **Backup:** Automated daily at 2:00 AM (7-day retention)

**Admin User:**
- **Username:** agames
- **Email:** agames.app.dev@gmail.com
- **Dashboard:** https://games.agames.cv/customadmin/

**Test User:**
- **Email:** ramy41599@gmail.com
- **Verified:** ✅ Yes

---

## Backup & Recovery

### Automated Backups
- ✅ **Daily Backup:** 2:00 AM (7-day retention)
- ✅ **Weekly Backup:** Sundays 3:00 AM
- ✅ **Location:** `/root/backups/postgresql/`
- ✅ **Compression:** gzip (~75% reduction)
- ✅ **Size:** ~16KB per backup

### Backup Commands
```bash
# Create manual backup
/root/game/scripts/backup_database.sh

# List available backups
/root/game/scripts/restore_database.sh

# Restore from backup
/root/game/scripts/restore_database.sh /root/backups/postgresql/agames_backup_YYYYMMDD_HHMMSS.sql.gz

# Manage backups (interactive)
/root/game/scripts/manage_backups.sh
```

**Documentation:** [DATABASE_BACKUP_SYSTEM.md](./docs/deployment/DATABASE_BACKUP_SYSTEM.md)

---

## Performance Metrics

### API Response Times
| Endpoint | Cache Miss | Cache Hit | Improvement |
|----------|-----------|-----------|-------------|
| `/api/games/` | ~307ms | ~2ms | **99.3%** |
| `/api/emulators/` | ~7.5ms | ~2.4ms | **68%** |

### Cache Statistics
- **Hit Rate:** 73%
- **Keyspace Hits:** 119
- **Keyspace Misses:** 44

### Server Load
- **CPU Load:** 0.14 (1-min avg)
- **Memory Used:** 1.9GB / 7.8GB (24%)
- **Disk Used:** 2.5GB / 251GB (1%)

---

## Maintenance Tasks

### Regular Tasks
- ✅ Monitor server resources (CPU, RAM, Disk)
- ✅ Check error logs daily
- ✅ Database backups (automated daily at 2:00 AM)
- ✅ Update dependencies monthly
- ✅ Review cache hit rates
- ✅ Monitor user activity
- ✅ Test backup restoration (monthly recommended)

### Database Backup
```bash
# Manual backup
sudo -u postgres pg_dump agames_db > backup_$(date +%Y%m%d).sql

# Automated backup (setup cron)
0 2 * * * sudo -u postgres pg_dump agames_db > /backups/agames_$(date +\%Y\%m\%d).sql
```

### Clear Cache
```bash
# Clear all Redis cache
redis-cli FLUSHDB

# Clear Django cache
cd /root/game
source venv/bin/activate
python manage.py shell -c "from django.core.cache import cache; cache.clear()"
```

---

## Upcoming Enhancements

### High Priority
1. **SSL/HTTPS Certificate**
   - Install Let's Encrypt certificate
   - Force HTTPS redirects
   - Enable secure cookies

2. **Database Backups**
   - Automated daily backups
   - Backup rotation (keep 7 days)
   - Off-site backup storage

3. **Monitoring & Alerting**
   - Setup Prometheus + Grafana
   - Configure error tracking (Sentry)
   - Uptime monitoring

### Medium Priority
1. CDN for static/media files
2. Celery for background tasks
3. Database query optimization (add indexes)
4. API versioning
5. Automated testing suite

### Low Priority
1. Docker containerization
2. CI/CD pipeline
3. Staging environment
4. Load balancer setup
5. Multi-region deployment

---

## Support

### Issues & Bug Reports
Create a support ticket via:
- **API:** `POST /api/support/tickets/`
- **Dashboard:** https://games.agames.cv/customadmin/support/

### Contact
- **Email:** agames.app.dev@gmail.com
- **Server IP:** 152.53.206.21
- **SSH Access:** root@152.53.206.21 (port 22)

---

## License

Proprietary - All rights reserved

---

## Changelog

### v1.0.0 (December 5, 2025)
- ✅ Initial production deployment
- ✅ PostgreSQL database setup
- ✅ Redis caching implemented (99% performance improvement)
- ✅ Gunicorn + Nginx configured
- ✅ UFW firewall enabled
- ✅ Security hardening (Argon2, headers, rate limiting)
- ✅ Google OAuth integration
- ✅ OTP email verification system
- ✅ Custom admin dashboard
- ✅ API documentation (Swagger/ReDoc)
- ✅ Support ticket system
- ✅ Push notifications (FCM)
- ✅ Advanced search with subsequence matching
- ✅ `open_outside` emulator attribute added

---

**Last Updated:** December 5, 2025  
**Maintained By:** AGames Development Team  
**Server Status:** 🟢 Operational
