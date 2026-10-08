# AGames Project - Deployment Summary

## 🚀 Server Information
- **Server IP:** 152.53.206.21
- **Environment:** Production
- **Python Version:** 3.13
- **Django Version:** 4.2.7
- **Database:** PostgreSQL (agames_db)

## 🔐 Admin Access
- **Custom Admin URL:** http://152.53.206.21/customadmin/login/
- **Username:** agames
- **Email:** agames.app.dev@gmail.com
- **Password:** (Set during deployment)

## 📡 API Endpoints

### Documentation
- API Docs (Swagger UI): http://152.53.206.21/api/docs/
- API Schema (OpenAPI): http://152.53.206.21/api/schema/

### Games
- Games List: GET http://152.53.206.21/api/games/
- Game Detail: GET http://152.53.206.21/api/games/{id}/
- Emulators List: GET http://152.53.206.21/api/emulators/
- Emulator Detail: GET http://152.53.206.21/api/emulators/{id}/

### Users
- Register: POST http://152.53.206.21/api/users/register/
- Login: POST http://152.53.206.21/api/users/login/
- Profile: GET http://152.53.206.21/api/users/profile/ (requires auth)
- Update Profile: PUT http://152.53.206.21/api/users/profile/ (requires auth)
- Verify OTP: POST http://152.53.206.21/api/users/verify-otp/
- Resend OTP: POST http://152.53.206.21/api/users/resend-otp/

### Subscriptions
- Plans List: GET http://152.53.206.21/api/plans/
- My Subscription: GET http://152.53.206.21/api/subscriptions/my-subscription/ (requires auth)
- Subscribe: POST http://152.53.206.21/api/subscriptions/subscribe/ (requires auth)
- Cancel: POST http://152.53.206.21/api/subscriptions/cancel/ (requires auth)

### Payments
- Create Payment: POST http://152.53.206.21/api/payments/create/ (requires auth)
- Payment History: GET http://152.53.206.21/api/payments/history/ (requires auth)

### Pages
- Page Detail: GET http://152.53.206.21/api/pages/{title}/
  - Example: /api/pages/about/, /api/pages/privacy/, etc.

### Notifications
- Device Tokens: GET http://152.53.206.21/api/notifications/devices/ (requires auth)
- Register Device: POST http://152.53.206.21/api/notifications/devices/ (requires auth)
- Notification Logs: GET http://152.53.206.21/api/notifications/logs/ (requires auth)

### Support
- Submit Message: POST http://152.53.206.21/api/support/api/messages/
- Support Messages: GET http://152.53.206.21/api/support/api/messages/ (requires auth)

## 🛠️ Services Running
- ✅ Gunicorn (Application Server)
- ✅ Nginx (Web Server)
- ✅ PostgreSQL (Database)
- ✅ Redis (Cache)

## 📁 Project Structure
```
/root/game/
├── customadmin/          # Custom admin dashboard
├── games/                # Games and emulators app
├── gamezone/             # Main Django project
├── notifications/        # Push notifications
├── pages/                # Static pages (about, privacy, etc.)
├── payments/             # Payment processing
├── subscriptions/        # Subscription management
├── support/              # Customer support
├── users/                # User management
├── staticfiles/          # Collected static files
├── media/                # User uploaded files
├── venv/                 # Python virtual environment
├── manage.py             # Django management
├── requirements.txt      # Python dependencies
└── start_gunicorn.sh     # Gunicorn startup script
```

## 🔧 Useful Commands

### Service Management
```bash
# Restart application
sudo systemctl restart gunicorn

# Restart web server
sudo systemctl restart nginx

# Check service status
sudo systemctl status gunicorn
sudo systemctl status nginx

# View logs
sudo journalctl -u gunicorn -f
sudo journalctl -u nginx -f
```

### Django Management
```bash
# Activate virtual environment
cd /root/game && source venv/bin/activate

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Django shell
python manage.py shell
```

### Database Management
```bash
# Access PostgreSQL
sudo -u postgres psql -d agames_db

# Backup database
pg_dump -U agames_user agames_db > backup.sql

# Restore database
psql -U agames_user agames_db < backup.sql
```

## 🔒 Security Notes
1. DEBUG is set to False in production
2. ALLOWED_HOSTS is configured for the server IP
3. Static and media files are properly secured
4. Database uses dedicated user with limited permissions
5. CSRF protection is enabled
6. CORS is configured for allowed origins

## 📝 Environment Variables (.env)
- SECRET_KEY: Django secret key
- DEBUG: False (production)
- ALLOWED_HOSTS: *
- DATABASE_URL: PostgreSQL connection string
- GOOGLE_CLIENT_ID: OAuth credentials
- GOOGLE_CLIENT_SECRET: OAuth credentials
- EMAIL_HOST_USER: SMTP email
- EMAIL_HOST_PASSWORD: SMTP password
- FIREBASE_CREDENTIALS_PATH: Firebase service account

## 🎯 Next Steps
1. ✅ Add games and emulators via custom admin
2. ✅ Create pages (About, Privacy Policy, Terms of Service)
3. ✅ Configure Stripe payment keys (when ready)
4. ✅ Test mobile app integration
5. ✅ Set up SSL/HTTPS (optional but recommended)
6. ✅ Configure regular database backups
7. ✅ Monitor application logs

## 📊 Testing
Run the API test script:
```bash
bash /root/game/test_api_endpoints.sh
```

## 🐛 Troubleshooting
- If static files don't load: `python manage.py collectstatic`
- If database connection fails: Check DATABASE_URL in .env
- If Gunicorn won't start: Check logs with `sudo journalctl -u gunicorn -n 50`
- If Nginx shows 502: Restart Gunicorn and check socket permissions

---
**Deployment Date:** December 4, 2025
**Status:** ✅ Production Ready
