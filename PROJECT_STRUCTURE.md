# Project Structure

```
game/
├── .env                          # Environment variables (DO NOT COMMIT)
├── .env.example                  # Environment template
├── .gitignore                    # Git ignore rules
├── manage.py                     # Django management script
├── README.md                     # Main project documentation
├── requirements.txt              # Python dependencies
├── gunicorn_config.py           # Gunicorn configuration
├── start_gunicorn.sh            # Gunicorn startup script
├── serviceAccountKey.json       # Firebase credentials (DO NOT COMMIT)
│
├── _archive/                    # Archived documentation
│   ├── old deployment guides
│   ├── deprecated docs
│   └── legacy files
│
├── configs/                     # Server configuration files
│   ├── nginx_cpx22.conf        # Nginx configuration
│   ├── postgresql_cpx22.conf   # PostgreSQL settings
│   └── redis_cpx22.conf        # Redis configuration
│
├── docs/                        # Documentation
│   ├── api/                    # API documentation
│   ├── deployment/             # Deployment guides
│   ├── security/               # Security docs
│   ├── CACHING_FIX_SUMMARY.md
│   ├── CURRENT_STATUS.md
│   ├── DASHBOARD_SUMMARY.md
│   ├── GOOGLE_FIREBASE_OAUTH_INSTRUCTIONS.md
│   ├── GOOGLE_OAUTH_MOBILE_CLIENT_GUIDE.md
│   ├── INFRASTRUCTURE_IMPROVEMENTS_COMPLETE.md
│   ├── PROJECT_CLEANUP_SUMMARY.md
│   ├── RECOMMENDATIONS.md
│   ├── RESPONSIVE_DASHBOARD_COMPLETE.md
│   ├── RESPONSIVE_TESTING_CHECKLIST.md
│   ├── REVIEW_SYSTEM_GUIDE.md
│   ├── REVIEW_SYSTEM_SUMMARY.md
│   └── SSL_CONFIGURATION_COMPLETE.md
│
├── tests/                       # Test scripts
│   ├── run_all_tests.sh        # Comprehensive test suite
│   ├── demo_notification_system.py
│   ├── load_test.py
│   ├── test_all_endpoints.py
│   ├── test_all_features.sh
│   ├── test_cache_invalidation.py
│   ├── test_new_features.py
│   ├── test_notification_api.py
│   ├── test_optional_fields.sh
│   ├── test_review_system.sh
│   └── verify_review_system.sh
│
├── logs/                        # Application logs
│   ├── gunicorn/
│   ├── nginx/
│   └── django/
│
├── media/                       # User uploaded files
│   ├── profile_pictures/
│   └── game_images/
│
├── staticfiles/                 # Collected static files (production)
│   ├── css/
│   ├── js/
│   ├── images/
│   └── admin/
│
├── scripts/                     # Utility scripts
│   ├── import_games.py
│   └── management commands
│
├── customadmin/                # Custom admin dashboard
│   ├── __init__.py
│   ├── apps.py
│   ├── urls.py
│   ├── views.py
│   ├── forms.py
│   ├── static/                 # Admin static files
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   ├── templates/              # Admin templates
│   │   └── customadmin/
│   │       ├── base.html
│   │       ├── dashboard.html
│   │       ├── game_form.html
│   │       ├── game_list.html
│   │       ├── notification_send.html
│   │       └── ...
│   ├── management/
│   │   └── commands/
│   └── templatetags/
│
├── games/                       # Games app
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py               # Game, GameReview, Genre models
│   ├── serializers.py          # DRF serializers
│   ├── views.py                # API views
│   ├── urls.py                 # URL routing
│   ├── signals.py              # Django signals
│   ├── tests.py
│   └── migrations/
│
├── users/                       # User management
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py               # User, UserProfile models
│   ├── serializers.py
│   ├── views.py                # Auth, profile views
│   ├── urls.py
│   ├── google_auth.py          # Google OAuth
│   ├── tests.py
│   └── migrations/
│
├── notifications/               # Notification system
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py               # DeviceToken, Notification, NotificationLog
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── fcm_service.py          # Firebase Cloud Messaging
│   ├── signals.py
│   ├── tests.py
│   └── migrations/
│
├── payments/                    # Payment processing
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py               # Payment, Transaction models
│   ├── serializers.py
│   ├── views.py                # Stripe integration
│   ├── urls.py
│   ├── tests.py
│   └── migrations/
│
├── subscriptions/               # Subscription system
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py               # Subscription, Plan models
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── tests.py
│   └── migrations/
│
├── support/                     # Support/help desk
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py               # Ticket, FAQ models
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── tests.py
│   └── migrations/
│
├── pages/                       # Static pages
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── migrations/
│
├── gamezone/                    # Main project settings
│   ├── __init__.py
│   ├── settings.py             # Django settings
│   ├── urls.py                 # Root URL configuration
│   ├── wsgi.py                 # WSGI config
│   └── asgi.py                 # ASGI config
│
└── venv/                        # Virtual environment (DO NOT COMMIT)
    └── ...

Feature-specific Documentation:
├── NEW_FEATURES_COMPLETE.md          # Recent features documentation
├── HOW_NOTIFICATIONS_WORK.md         # Notification system guide
├── WHY_DEVICE_TOKENS_REQUIRED.md     # Device token explanation
├── NOTIFICATION_FLOW_VISUAL.md       # Visual notification flow
├── QUICK_REFERENCE.md                # Quick reference guide
├── REVIEW_SYSTEM_COMPLETE.md         # Review system docs
└── dkim_public_key.txt              # Email DKIM key
```

## Key Files Explained

### Configuration Files

- **.env**: Environment variables (database, API keys, secrets)
- **gunicorn_config.py**: Gunicorn WSGI server configuration
- **serviceAccountKey.json**: Firebase service account credentials

### Application Structure

Each app follows Django's standard structure:
- **models.py**: Database models
- **views.py**: Request handlers
- **serializers.py**: API serialization (Django REST Framework)
- **urls.py**: URL routing
- **admin.py**: Django admin configuration
- **signals.py**: Django signals for automated tasks
- **migrations/**: Database migrations

### Static Files

- **customadmin/static/**: Custom admin dashboard assets
- **staticfiles/**: Collected static files for production (generated)

### Documentation

- **README.md**: Main project overview
- **docs/**: Detailed documentation by category
- **Feature docs**: Specific feature documentation (notifications, reviews, etc.)
- **_archive/**: Old/deprecated documentation

### Tests

- **tests/**: All test scripts and utilities
- **run_all_tests.sh**: Comprehensive system test

## Important Notes

### Files to NEVER commit:
- `.env` (contains secrets)
- `serviceAccountKey.json` (Firebase credentials)
- `venv/` (virtual environment)
- `__pycache__/` (Python cache)
- `*.pyc` (compiled Python)
- `staticfiles/` (generated files)
- `media/` (user uploads)

### Files to always commit:
- `.env.example` (template without secrets)
- `requirements.txt` (dependencies)
- All `.py` files (source code)
- `configs/` (server configurations)
- Documentation files
- Migration files

## Development Workflow

1. Activate virtual environment: `source venv/bin/activate`
2. Make changes to code
3. Create migrations: `python manage.py makemigrations`
4. Apply migrations: `python manage.py migrate`
5. Test changes: `python manage.py runserver`
6. Run tests: `./tests/run_all_tests.sh`
7. Collect static: `python manage.py collectstatic`
8. Restart services: `sudo systemctl restart gunicorn`

## Production Deployment

1. Pull latest code: `git pull origin main`
2. Activate venv: `source venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Run migrations: `python manage.py migrate`
5. Collect static: `python manage.py collectstatic --noinput`
6. Restart Gunicorn: `sudo systemctl restart gunicorn`
7. Check status: `sudo systemctl status gunicorn`
