# Security Configuration for AGames Production

# Add these to .env for HTTPS (when SSL is configured)
# SESSION_COOKIE_SECURE=True
# CSRF_COOKIE_SECURE=True
# SECURE_SSL_REDIRECT=True
# SECURE_HSTS_SECONDS=31536000
# SECURE_HSTS_INCLUDE_SUBDOMAINS=True
# SECURE_HSTS_PRELOAD=True

# Database Connection Pool (add to settings.py when scaling)
# DATABASES['default']['CONN_MAX_AGE'] = 600
# DATABASES['default']['CONN_HEALTH_CHECKS'] = True

# Rate Limiting (already configured in settings.py)
# - Login: 8/minute
# - OTP: 3/minute
# - Authenticated users: 50/minute
# - Anonymous users: 20/minute

# File Upload Security (add to settings.py if needed)
# DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
# FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
# ALLOWED_UPLOAD_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.zip']

# Admin Security
# - Custom admin at /customadmin/ (not /admin/)
# - Only superusers can access
# - Login required for all admin views

# API Security
# - Token authentication required for user-specific endpoints
# - CORS configured for specific origins
# - CSRF protection enabled
# - Rate limiting active

# Password Requirements
# - Minimum 8 characters (configurable in User model)
# - Uses Argon2 hashing (most secure)
# - Password validation enabled

# Session Security
# - HTTPOnly cookies (prevents XSS)
# - SameSite=Lax (prevents CSRF)
# - 2-week expiration
# - Secure flag when HTTPS enabled
