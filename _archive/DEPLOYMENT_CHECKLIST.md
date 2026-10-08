# ✅ AGames Deployment Checklist

## 📋 Pre-Deployment

### Code Preparation
- [x] All tests passing (16/16) ✅
- [x] Database optimizations applied ✅
- [x] Migrations created ✅
- [ ] Code pushed to GitHub
- [ ] Production branch created
- [ ] `.env.example` file created

### Environment Configuration
- [ ] Domain name registered
- [ ] DNS configured to point to server IP
- [ ] SSL certificate plan (Let's Encrypt recommended)
- [ ] Email service verified (Gmail SMTP working)
- [ ] Google OAuth credentials verified

---

## 🖥️ Server Setup

### VPS Provider
- [ ] VPS purchased (Hetzner CX21 recommended)
- [ ] Server IP obtained
- [ ] SSH access configured
- [ ] Server OS: Ubuntu 22.04 LTS

### System Packages
- [ ] System updated (`apt update && apt upgrade`)
- [ ] Python 3.10+ installed
- [ ] PostgreSQL 14+ installed
- [ ] Nginx installed
- [ ] Redis installed
- [ ] Supervisor installed
- [ ] Git installed

---

## 🗄️ Database Setup

- [ ] PostgreSQL database created (`agames_db`)
- [ ] Database user created (`agames_user`)
- [ ] Strong password set for database
- [ ] Database permissions granted
- [ ] PostgreSQL performance tuned (optional)
- [ ] Database connection tested

---

## 📦 Application Deployment

### Project Setup
- [ ] Repository cloned to server
- [ ] Virtual environment created
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Gunicorn installed
- [ ] psycopg2-binary installed

### Django Configuration
- [ ] `.env` file created with all variables
- [ ] `SECRET_KEY` generated (new, not from git)
- [ ] `DEBUG=False` set
- [ ] `ALLOWED_HOSTS` configured
- [ ] `DATABASE_URL` configured (PostgreSQL)
- [ ] Email settings verified
- [ ] Google OAuth settings configured
- [ ] CORS settings configured

### Django Operations
- [ ] Static files collected (`collectstatic`)
- [ ] Migrations applied (`migrate`)
- [ ] Superuser created (`createsuperuser`)
- [ ] Test server run successful

---

## 🔥 Web Server Setup

### Gunicorn
- [ ] Gunicorn socket file created
- [ ] Gunicorn service file created
- [ ] Logs directory created
- [ ] Gunicorn started and enabled
- [ ] Gunicorn status verified (active)

### Nginx
- [ ] Nginx configuration file created
- [ ] Configuration syntax tested (`nginx -t`)
- [ ] Site enabled (symlink created)
- [ ] File permissions set correctly
- [ ] Nginx restarted
- [ ] HTTP access working (port 80)

---

## 🔒 Security

### SSL/HTTPS
- [ ] Certbot installed
- [ ] SSL certificate obtained
- [ ] Auto-renewal configured
- [ ] HTTPS working
- [ ] HTTP redirects to HTTPS

### Firewall
- [ ] UFW enabled
- [ ] SSH allowed
- [ ] HTTP/HTTPS allowed
- [ ] Firewall status verified

### Passwords & Secrets
- [ ] All passwords are strong (16+ chars)
- [ ] `SECRET_KEY` is unique and secure
- [ ] Database password is strong
- [ ] Redis password set (optional)
- [ ] No secrets in git repository

---

## 🔧 Optional Services

### Redis
- [ ] Redis installed
- [ ] Redis started and enabled
- [ ] Redis password configured
- [ ] Redis connection tested
- [ ] `REDIS_URL` in `.env`

### Supervisor
- [ ] Supervisor config created
- [ ] Supervisor updated
- [ ] Process status verified

---

## 🧪 Testing

### API Endpoints
- [ ] `/api/` accessible
- [ ] `/api/users/register/` works
- [ ] `/api/users/login/` works
- [ ] `/api/games/` works
- [ ] `/api/emulators/` works

### Admin Panels
- [ ] `/admin/` accessible
- [ ] Can login to Django admin
- [ ] `/customadmin/` accessible
- [ ] Can login to custom admin

### Features
- [ ] User registration works
- [ ] OTP email received
- [ ] Email verification works
- [ ] User login works
- [ ] Password reset works
- [ ] Google OAuth works
- [ ] Profile picture upload works
- [ ] Game cover upload works
- [ ] Premium status toggle works
- [ ] Game download works
- [ ] Game love/unlike works
- [ ] Game rating works

### Performance
- [ ] Page load time < 500ms
- [ ] Database queries optimized
- [ ] Static files loading fast
- [ ] No 500 errors in logs

---

## 💾 Backup & Monitoring

### Backups
- [ ] Database backup script created
- [ ] Backup cron job configured
- [ ] Test backup/restore performed
- [ ] Media files backup configured
- [ ] Backup storage location verified

### Monitoring
- [ ] Health check endpoint created
- [ ] Error logs location known
- [ ] Access logs location known
- [ ] Log rotation configured

---

## 📱 Mobile App Integration

### API Configuration
- [ ] Base URL configured in mobile app
- [ ] API authentication tested
- [ ] File uploads tested
- [ ] Push notifications configured (if applicable)

### CORS
- [ ] Frontend domain added to `CORS_ALLOWED_ORIGINS`
- [ ] Preflight requests working
- [ ] Cookies/credentials working (if needed)

---

## 📚 Documentation

- [ ] API documentation accessible (`/api/schema/swagger-ui/`)
- [ ] Deployment guide available
- [ ] Environment variables documented
- [ ] Backup procedures documented
- [ ] Update procedures documented

---

## ✅ Final Verification

### Functionality
- [ ] All core features working
- [ ] No console errors
- [ ] No server errors (500)
- [ ] Forms submitting correctly
- [ ] Files uploading correctly

### Security
- [ ] HTTPS enforced
- [ ] CORS configured properly
- [ ] SQL injection protected (Django ORM)
- [ ] XSS protected (Django templates)
- [ ] CSRF protection enabled

### Performance
- [ ] Fast response times (< 500ms)
- [ ] Caching working (if enabled)
- [ ] Database queries optimized
- [ ] Static files compressed

### SEO & Headers
- [ ] Security headers configured
- [ ] Gzip compression enabled
- [ ] Cache headers set

---

## 🎯 Post-Deployment

### Within 24 Hours
- [ ] Monitor error logs
- [ ] Check server resource usage
- [ ] Verify emails are being sent
- [ ] Test all critical features
- [ ] Set up uptime monitoring

### Within 1 Week
- [ ] Review backup logs
- [ ] Check SSL certificate expiry
- [ ] Monitor database performance
- [ ] Review user feedback
- [ ] Optimize any slow queries

---

## 🚨 Emergency Contacts

### Service Providers
- **VPS Provider**: _________________
- **Domain Registrar**: _________________
- **Email Service**: Gmail SMTP
- **DNS Provider**: _________________

### Access Information
- **Server IP**: _________________
- **Domain**: _________________
- **SSH User**: agames
- **Database Name**: agames_db
- **Database User**: agames_user

---

## 📞 Troubleshooting Quick Reference

### 502 Bad Gateway
```bash
sudo systemctl status gunicorn
sudo systemctl restart gunicorn
```

### Static Files Not Loading
```bash
python manage.py collectstatic --noinput
sudo systemctl restart nginx
```

### Database Connection Error
```bash
sudo systemctl status postgresql
# Check .env DATABASE_URL
```

### Email Not Sending
```bash
# Check Django logs
# Verify Gmail app password
# Test SMTP connection
```

---

## 📊 Success Metrics

After deployment, track:
- [ ] 99.9% uptime
- [ ] < 500ms average response time
- [ ] 0 critical errors in 24 hours
- [ ] All automated tests passing
- [ ] Successful user registrations
- [ ] Successful OAuth logins

---

**Deployment Started**: _______________
**Deployment Completed**: _______________
**Deployed By**: _______________
**Server IP**: _______________
**Domain**: _______________

---

## 🎉 Ready for Production!

Once all items are checked, your AGames API is production-ready!

**Live URL**: https://your-domain.com  
**Admin**: https://your-domain.com/admin/  
**API Docs**: https://your-domain.com/api/schema/swagger-ui/
