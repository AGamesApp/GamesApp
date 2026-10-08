# API Documentation Updates - December 5, 2025

## New Sections Added

### 1. Health Check Endpoint ✅
**Location:** Section 2  
**Endpoint:** `GET /health/`

**Purpose:**
- Monitor system health (database, cache, filesystem)
- Uptime monitoring integration (UptimeRobot, Pingdom)
- Load balancer health checks

**Example:**
```bash
curl http://152.53.206.21/health/
```

**Response:**
```json
{
  "status": "healthy",
  "checks": {
    "database": "ok",
    "cache": "ok",
    "filesystem": "ok"
  }
}
```

---

### 2. Password Reset Flow ✅
**Location:** Users & Auth section (endpoints 6-8)

#### 6. Request Password Reset
- **Endpoint:** `POST /api/users/password-reset/request/`
- **Purpose:** Send OTP to user's email
- **Rate Limit:** 3 requests/minute

#### 7. Verify Password Reset OTP
- **Endpoint:** `POST /api/users/password-reset/verify-otp/`
- **Purpose:** Validate the OTP before password change

#### 8. Reset Password
- **Endpoint:** `POST /api/users/password-reset/reset/`
- **Purpose:** Update password using verified OTP

**Complete Flow Example:**
```bash
# Step 1: Request OTP
curl -X POST http://152.53.206.21/api/users/password-reset/request/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'

# Step 2: Verify OTP (from email)
curl -X POST http://152.53.206.21/api/users/password-reset/verify-otp/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "otp": "970521"}'

# Step 3: Reset Password
curl -X POST http://152.53.206.21/api/users/password-reset/reset/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "otp": "970521",
    "new_password": "NewPassword123!",
    "confirm_password": "NewPassword123!"
  }'
```

---

### 3. Change Password (Authenticated) ✅
**Location:** Users & Auth section (endpoint 9)

**Endpoint:** `POST /api/users/change-password/`  
**Purpose:** Change password for logged-in users

**Example:**
```bash
curl -X POST http://152.53.206.21/api/users/change-password/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "OldPassword123!",
    "new_password": "NewPassword123!",
    "confirm_password": "NewPassword123!"
  }'
```

---

### 4. Email Configuration ✅
**Location:** New section before Changelog

**Covers:**
- SMTP settings (Gmail configuration)
- Email types sent (OTP, password reset, support)
- Email rate limits
- Customization instructions

**Current SMTP Config:**
- **Server:** smtp.gmail.com:587
- **Sender:** agames.app.dev@gmail.com
- **App Password:** ukunsishtslgxyez

**Email Types:**
1. **Email Verification OTP** - 6-digit code, valid 10 minutes
2. **Password Reset OTP** - 6-digit code, valid 10 minutes
3. **Support Ticket Notifications** - Ticket updates

---

### 5. Firebase Cloud Messaging (FCM) ✅
**Location:** New section before Changelog

**Details:**
- **Service Account:** firebase-adminsdk-fbsvc@agames-21123.iam.gserviceaccount.com
- **Project ID:** agames-21123
- **Client ID:** 114457783983123047230
- **Credentials:** `/root/game/serviceAccountKey.json`

**Notification Types:**
- New game releases
- Subscription updates
- Support ticket replies
- System announcements

---

### 6. Updated Changelog ✅
**Added infrastructure improvements:**
- Redis caching (73% hit rate)
- 7 Gunicorn workers (1,000+ concurrent capacity)
- Gzip compression (40-60% reduction)
- 4GB swap space for stability
- Health check endpoint

---

## Updated Table of Contents

```markdown
1. Authentication
2. Health Check ← NEW
3. Users & Auth (expanded with password reset)
4. Games
5. Emulators
6. Subscriptions
7. Notifications
8. Support
9. Pages
10. Search Techniques
11. Caching
12. Email Configuration ← NEW
```

---

## Password Requirements (Documented)

✅ Minimum 8 characters  
✅ Uppercase and lowercase letters  
✅ At least one number  
✅ At least one special character

---

## Rate Limits (Updated)

- **Logged-in users:** 50 requests/minute
- **Anonymous users:** 20 requests/minute
- **Login endpoint:** 8 requests/minute
- **OTP resend:** 3 requests/minute
- **Password reset:** 3 requests/minute ← NEW

---

## Testing Endpoints

### Test Password Reset
```bash
# User: ramy41599@gmail.com
# Current password: NewPassword123!

# 1. Request OTP
curl -X POST http://152.53.206.21/api/users/password-reset/request/ \
  -H "Content-Type: application/json" \
  -d '{"email": "ramy41599@gmail.com"}'

# 2. Check OTP in database or email
# 3. Verify and reset
```

### Test Health Check
```bash
curl http://152.53.206.21/health/
```

### Test Login
```bash
curl -X POST http://152.53.206.21/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "ramy41599@gmail.com",
    "password": "NewPassword123!"
  }'
```

---

## Summary Statistics

**Total Lines:** 1,575 (was 1,261)  
**New Lines Added:** 314  
**New Endpoints Documented:** 4
- Password reset request
- Password reset OTP verification
- Password reset completion
- Change password (authenticated)

**New Sections:** 3
- Health Check
- Email Configuration
- Firebase Cloud Messaging

**Updated Sections:** 2
- Table of Contents
- Changelog

---

## Next Steps

1. ✅ **Documentation complete** - All endpoints documented
2. 🔄 **Consider adding:**
   - API versioning strategy
   - WebSocket endpoints (if any)
   - File upload examples
   - Batch operation endpoints
   - GraphQL schema (if implemented)

3. 🎯 **Recommended improvements:**
   - Add Postman collection export
   - Create example client code (Python, JavaScript)
   - Add rate limit bypass for testing
   - Document webhook endpoints (if any)

---

**Last Updated:** December 5, 2025  
**Documentation Version:** 1.1  
**API Version:** 1.0
