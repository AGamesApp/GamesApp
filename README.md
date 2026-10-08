# Game Zone - Backend API

A Django-based backend system for a retro gaming platform with push notifications, user management, and game catalog.

## 🚀 Features

### Core Features
- **Game Management**: Browse, search, and filter 2000+ retro games
- **User Authentication**: Google OAuth, email/password, OTP verification
- **Push Notifications**: Firebase Cloud Messaging for all users
- **Review System**: Rate and review games
- **Download Tracking**: Track game downloads
- **Favorites/Wishlist**: Save and love games
- **Subscription System**: Premium memberships
- **Payment Integration**: Stripe payment processing
- **Admin Dashboard**: Custom admin panel for management

### Recent Features
- ✅ Game description field (editable from dashboard)
- ✅ Broadcast notifications to ALL users (registered + anonymous)
- ✅ Database notification storage for registered users
- ✅ Notification type system (normal, fix, update, error)
- ✅ Smart caching with auto-invalidation
- ✅ Optimized for high concurrency (200+ users)

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [API Documentation](#api-documentation)
- [Notification System](#notification-system)
- [Admin Dashboard](#admin-dashboard)
- [Deployment](#deployment)
- [Testing](#testing)
- [Documentation](#documentation)

## 🏁 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 14+
- Redis 7+
- Nginx
- Gunicorn

### Installation

```bash
# Clone repository
git clone https://github.com/Ramyrashad127/game.git
cd game

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your credentials

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Start development server
python manage.py runserver
```

### Production Deployment

```bash
# Start Gunicorn
sudo systemctl start gunicorn
sudo systemctl enable gunicorn

# Start Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Check status
sudo systemctl status gunicorn
sudo systemctl status nginx
```

## 📡 API Documentation

### Base URL
```
Production: https://games.agames.cv/api/
Development: http://localhost:8000/api/
```

### Main Endpoints

#### Games
```bash
GET    /api/games/                    # List all games
GET    /api/games/{id}/               # Game details
GET    /api/games/search/?q=mario     # Search games
GET    /api/games/trending/           # Trending games
POST   /api/games/{id}/download/      # Track download
POST   /api/games/{id}/love/          # Love/unlike game
```

#### Authentication
```bash
POST   /api/auth/register/            # Register user
POST   /api/auth/login/               # Login
POST   /api/auth/google/              # Google OAuth
POST   /api/auth/verify-otp/          # Verify OTP
POST   /api/auth/logout/              # Logout
```

#### Notifications
```bash
GET    /api/notifications/            # List user notifications
GET    /api/notifications/unread/     # Get unread notifications
POST   /api/notifications/{id}/mark_read/  # Mark as read
POST   /api/notifications/mark_all_read/   # Mark all as read
POST   /api/device-tokens/            # Register device for push
```

#### Reviews
```bash
GET    /api/reviews/                  # List reviews
POST   /api/reviews/                  # Create review
PUT    /api/reviews/{id}/             # Update review
DELETE /api/reviews/{id}/             # Delete review
```

### Authentication

All user-specific endpoints require authentication:

```bash
# Include token in header
Authorization: Token {your-auth-token}
```

## 🔔 Notification System

### How It Works

The system uses **Firebase Cloud Messaging (FCM)** to send push notifications to all users, including those without accounts.

#### For Mobile App Developers

```javascript
// React Native example
import messaging from '@react-native-firebase/messaging';

async function setupNotifications() {
  // Request permission
  await messaging().requestPermission();
  
  // Get device token
  const token = await messaging().getToken();
  
  // Register with backend
  await fetch('https://games.agames.cv/api/device-tokens/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      token: token,
      platform: Platform.OS, // 'ios' or 'android'
      device_id: await DeviceInfo.getUniqueId()
    })
  });
}

// Call on app start
setupNotifications();
```

#### Notification Flow

```
1. User downloads app
   ↓
2. Firebase creates device token automatically
   ↓
3. App sends token to backend
   ↓
4. Backend stores token
   ↓
5. Admin sends notification
   ↓
6. Push sent to ALL devices
   + Database copy for registered users
```

#### Notification Types

- **📢 Normal**: General announcements
- **🔧 Fix**: Bug fixes
- **🆙 Update**: New features/games
- **⚠️ Error**: Important alerts

### Admin Dashboard

Access: `https://games.agames.cv/custom-admin/`

#### Send Notification
1. Go to: `/custom-admin/notifications/send/`
2. Fill form:
   - Title (required)
   - Message (required)
   - Type (normal, fix, update, error)
   - Image URL (optional)
3. Click "Send Notification"

#### Manage Games
- Add/Edit games: `/custom-admin/games/`
- Edit description field
- Upload images
- Set emulator type

#### View Statistics
- Dashboard: `/custom-admin/`
- User stats
- Game stats
- Download tracking
- Review analytics

## 🚀 Deployment

### Server Requirements
- **CPU**: 3+ vCPU
- **RAM**: 4GB+
- **Storage**: 40GB+
- **OS**: Ubuntu 22.04+

### Services Configuration

#### Gunicorn
```bash
# /etc/systemd/system/gunicorn.service
Workers: 7
Worker Class: sync
Timeout: 60
```

#### Nginx
```bash
# /etc/nginx/sites-available/gamezone
SSL: Enabled (Let's Encrypt)
HTTP/2: Enabled
Gzip: Enabled
```

#### PostgreSQL
```bash
Max Connections: 100
Shared Buffers: 1GB
```

#### Redis
```bash
Max Memory: 512MB
Policy: allkeys-lru
```

### Restart Services

```bash
# Restart Gunicorn
sudo systemctl restart gunicorn

# Restart Nginx
sudo systemctl restart nginx

# Check logs
sudo journalctl -u gunicorn -n 50
sudo journalctl -u nginx -n 50
```

## 🧪 Testing

### Run All Tests

```bash
cd /root/game/tests

# Test all features
./test_all_features.sh

# Test notifications
python test_notification_api.py

# Test new features
python test_new_features.py

# Load testing
python load_test.py

# Demo notification system
python demo_notification_system.py
```

### Manual Testing

```bash
# Check API health
curl https://games.agames.cv/api/games/

# Test authentication
curl -X POST https://games.agames.cv/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# Test notifications (requires auth token)
curl https://games.agames.cv/api/notifications/ \
  -H "Authorization: Token your-token-here"
```

## 📚 Documentation

### Main Documentation
- **README.md** (this file) - Project overview
- **docs/** - Detailed documentation
  - API reference
  - Deployment guides
  - Security documentation

### Feature Documentation
- **NEW_FEATURES_COMPLETE.md** - Recent features
- **HOW_NOTIFICATIONS_WORK.md** - Notification system explained
- **WHY_DEVICE_TOKENS_REQUIRED.md** - Device token explanation
- **QUICK_REFERENCE.md** - Quick reference guide

### Archive
- **_archive/** - Old documentation and deprecated files

## 🔧 Maintenance

### Database Migrations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Check migration status
python manage.py showmigrations
```

### Clear Cache

```bash
# Clear Redis cache
redis-cli FLUSHALL

# Or from Django
python manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()
```

### Backup Database

```bash
# Backup
pg_dump -U postgres game_db > backup.sql

# Restore
psql -U postgres game_db < backup.sql
```

## 📊 Performance

### Current Capacity
- **Concurrent Users**: 200+
- **Success Rate**: 100%
- **Response Time**: <200ms (cached), <500ms (uncached)
- **Database Size**: ~2GB (2000+ games)

### Optimization Features
- Smart caching with Redis
- Database query optimization
- Connection pooling
- Static file compression
- CDN-ready setup

## 🔒 Security

### Features
- HTTPS/SSL encryption
- CSRF protection
- SQL injection prevention
- XSS protection
- Rate limiting
- Secure password hashing
- Token-based authentication
- CORS configuration

### Security Headers
```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 License

This project is proprietary and confidential.

## 👥 Support

- **Issues**: GitHub Issues
- **Email**: support@games.agames.cv
- **Documentation**: See `/docs` folder

## 🎯 Roadmap

### Planned Features
- [ ] Scheduled notifications
- [ ] User notification preferences
- [ ] Rich notifications with actions
- [ ] Notification analytics
- [ ] Targeted notification segments
- [ ] Deep linking support

### In Progress
- ✅ All core features complete
- ✅ Notification system operational
- ✅ Performance optimized

## 📈 Project Status

**Version**: 1.0.0
**Status**: Production Ready ✅
**Last Updated**: December 8, 2025

### System Health
- ✅ Backend API: Operational
- ✅ Admin Dashboard: Operational
- ✅ Notifications: Operational
- ✅ Database: Healthy
- ✅ Cache: Operational
- ⏳ Mobile App: In Development

---

**Made with ❤️ for retro gaming enthusiasts**
