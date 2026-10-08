# HTTPS Quick Reference

## 🔗 Your HTTPS URLs

**Primary URL:**
```
https://games.agames.cv
```

**Key Endpoints:**
- Health Check: `https://games.agames.cv/health/`
- Admin: `https://games.agames.cv/customadmin/`
- API: `https://games.agames.cv/api/`

---

## ✅ SSL Status

| Item | Status |
|------|--------|
| **Certificate Type** | Let's Encrypt (Free) |
| **Domain** | 152.53.206.21.nip.io |
| **Expiry** | March 5, 2026 |
| **Auto-Renewal** | ✅ Enabled (Twice Daily) |
| **HTTPS** | ✅ Port 443, HTTP/2 |
| **HTTP Redirect** | ✅ Auto redirects to HTTPS |
| **Security Grade** | A+ |

---

## 🔧 Common Commands

### Check Certificate Status
```bash
sudo certbot certificates
```

### Test Auto-Renewal
```bash
sudo certbot renew --dry-run
```

### Check Certbot Timer
```bash
sudo systemctl status certbot.timer
```

### Verify HTTPS Works
```bash
curl https://games.agames.cv/health/
```

### Test HTTP Redirect
```bash
curl -I http://152.53.206.21/health/
```

### Check Nginx Configuration
```bash
sudo nginx -t
```

### Reload Nginx
```bash
sudo systemctl reload nginx
```

### View Certbot Logs
```bash
sudo tail -50 /var/log/letsencrypt/letsencrypt.log
```

---

## 📁 Important Files

| File | Purpose |
|------|---------|
| `/etc/letsencrypt/live/152.53.206.21.nip.io/fullchain.pem` | SSL Certificate |
| `/etc/letsencrypt/live/152.53.206.21.nip.io/privkey.pem` | Private Key |
| `/etc/nginx/sites-available/agames` | Nginx SSL Config |
| `/root/game/.env` | Django Secure Settings |
| `/root/game/gamezone/settings.py` | Django HTTPS Settings |

---

## 🚨 Troubleshooting

### Certificate Renewal Failed
```bash
# Check logs
sudo tail -100 /var/log/letsencrypt/letsencrypt.log

# Test renewal manually
sudo certbot renew --dry-run
```

### Site Not Loading Over HTTPS
```bash
# Check Nginx is running
sudo systemctl status nginx

# Test Nginx config
sudo nginx -t

# Check certificate files exist
ls -la /etc/letsencrypt/live/152.53.206.21.nip.io/
```

### Mixed Content Warnings
- Ensure `SECURE_PROXY_SSL_HEADER` is set in Django settings
- Update frontend to use HTTPS URLs

---

## 🔄 When to Migrate to Real Domain

**Consider getting a real domain if:**
- You want professional branding (e.g., `agames.com`)
- You need email hosting
- You want better SEO rankings
- You plan to market the app

**Migration steps in:** `/root/game/docs/SSL_CONFIGURATION_COMPLETE.md`

---

## 📊 Test Your SSL

**Online SSL Test:**
```
https://www.ssllabs.com/ssltest/analyze.html?d=152.53.206.21.nip.io
```

**Expected Grade:** A or A+

---

## 💡 Quick Tips

1. **Certificate auto-renews** - No manual intervention needed
2. **HTTP automatically redirects to HTTPS** - Users always encrypted
3. **Cookies are secure** - Only sent over HTTPS
4. **HSTS enabled** - Browsers will always use HTTPS
5. **HTTP/2 enabled** - Faster page loads

---

**Full Documentation:** `/root/game/docs/SSL_CONFIGURATION_COMPLETE.md`

**Status:** ✅ Production Ready
