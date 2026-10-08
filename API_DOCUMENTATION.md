# AGames API Documentation

**Base URL:** `https://games.agames.cv/api/`  
**Authentication:** DRF Token Auth — `Authorization: Token <token>`  
**Anti-Sharing Header:** `X-Session-Id: <session_id>` (required after login)

---

## Table of Contents

1. [Authentication & Users](#1-authentication--users)
   - [Register](#11-register)
   - [Verify OTP (Email Verification)](#12-verify-otp-email-verification)
   - [Resend OTP](#13-resend-otp)
   - [Login](#14-login)
   - [Logout](#15-logout)
   - [User Status (Premium Check)](#16-user-status-premium-check)
   - [User Profile](#17-user-profile)
   - [Update Profile Picture](#18-update-profile-picture)
   - [Change Password](#19-change-password)
2. [Password Reset](#2-password-reset)
   - [Request Reset OTP](#21-request-reset-otp)
   - [Verify Reset OTP](#22-verify-reset-otp)
   - [Reset Password](#23-reset-password)
3. [Google OAuth](#3-google-oauth)
4. [Google Play Payments](#4-google-play-payments)
   - [Verify Purchase](#41-verify-purchase)
5. [Anti-Sharing Enforcement](#5-anti-sharing-enforcement)
6. [Error Reference](#6-error-reference)

---

## 1. Authentication & Users

### 1.1 Register

Create a new account. A 6-digit OTP is sent to the provided email for verification.

```
POST /api/users/register/
```

**Request Body:**
```json
{
  "username": "john",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!"
}
```

**Success Response — `201 Created`:**
```json
{
  "message": "Registration successful. Please check your email for the verification code."
}
```

**Failure (email send error) — `500 Internal Server Error`:**
```json
{
  "error": "Failed to send verification email. Please try again."
}
```

> ⚠️ The OTP is **not** saved to the database until the email is delivered successfully. If the email fails, the user record is created but no OTP is stored — they must use Resend OTP.

---

### 1.2 Verify OTP (Email Verification)

Confirm email address with the 6-digit code received by email.

```
POST /api/users/verify-otp/
```

**Request Body:**
```json
{
  "email": "john@example.com",
  "otp": "482913"
}
```

**Success Response — `200 OK`:**
```json
{
  "message": "Email verified successfully. You can now login."
}
```

**Failure — `400 Bad Request`:**
```json
{
  "error": "Invalid or expired OTP."
}
```

> OTPs expire after **10 minutes**.

---

### 1.3 Resend OTP

Request a new verification OTP (e.g. if the previous one expired).

```
POST /api/users/resend-otp/
```

**Request Body:**
```json
{
  "email": "john@example.com"
}
```

**Success Response — `200 OK`:**
```json
{
  "message": "New verification code sent to your email."
}
```

**Already verified — `200 OK`:**
```json
{
  "message": "Email is already verified. You can login now."
}
```

**Rate limit:** 3 requests/hour per IP.

---

### 1.4 Login

Authenticates the user and returns a token + session ID.

```
POST /api/users/login/
```

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```

**Success Response — `200 OK`:**
```json
{
  "user": {
    "id": 5,
    "email": "john@example.com",
    "username": "john",
    "is_premium": false,
    "is_email_verified": true,
    "profile_picture": null,
    "premium_expiration": null
  },
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "session_id": "a3f2c1d0-5e6b-4a7c-8d9e-1b2f3c4d5e6f"
}
```

**Email not verified — `403 Forbidden`:**
```json
{
  "error": "Email verification required",
  "message": "Your email address is not verified. Please check your email inbox and verify your account before logging in.",
  "email": "john@example.com"
}
```

**Invalid credentials — `400 Bad Request`:**
```json
{
  "error": "Invalid credentials"
}
```

> ⚠️ **Important:** Every login **rotates** the auth token and `session_id`. Any previous device holding the old token will get `401 Unauthorized` on the next request. Store both `token` and `session_id` and send them on every request.

---

### 1.5 Logout

Invalidates the auth token and clears the session.

```
POST /api/users/logout/
Authorization: Token <token>
X-Session-Id: <session_id>
```

**Success Response — `200 OK`:**
```json
{
  "message": "Successfully logged out."
}
```

---

### 1.6 User Status (Premium Check)

Called every time the app opens or comes back to foreground. Auto-expires premium if the subscription date has passed.

```
GET /api/users/status/
Authorization: Token <token>
X-Session-Id: <session_id>
```

**Success Response — `200 OK`:**
```json
{
  "is_premium": true,
  "expiration_date": "2026-01-28T14:30:00Z",
  "email": "john@example.com",
  "username": "john"
}
```

```json
{
  "is_premium": false,
  "expiration_date": null,
  "email": "john@example.com",
  "username": "john"
}
```

> Call this endpoint on every app startup to keep the premium flag in sync.

---

### 1.7 User Profile

Retrieve or update the user's profile.

```
GET  /api/users/profile/
PUT  /api/users/profile/
PATCH /api/users/profile/
Authorization: Token <token>
X-Session-Id: <session_id>
```

**GET Response — `200 OK`:**
```json
{
  "id": 5,
  "email": "john@example.com",
  "username": "john",
  "is_premium": true,
  "is_email_verified": true,
  "profile_picture": "https://games.agames.cv/media/profiles/john.jpg",
  "premium_expiration": "2026-01-28T14:30:00Z"
}
```

**PATCH Request Body (partial update):**
```json
{
  "username": "john_updated"
}
```

---

### 1.8 Update Profile Picture

Upload or replace the profile picture.

```
POST /api/users/profile/picture/
Authorization: Token <token>
X-Session-Id: <session_id>
Content-Type: multipart/form-data
```

**Form Fields:**
| Field | Type | Required |
|-------|------|----------|
| `profile_picture` | File (image) | ✅ |

**Accepted types:** JPG, PNG, GIF, WEBP  
**Max size:** 5 MB

**Success Response — `200 OK`:**
```json
{
  "message": "Profile picture updated successfully",
  "profile_picture": "https://games.agames.cv/media/profiles/john.jpg"
}
```

---

### 1.9 Change Password

```
POST /api/users/change-password/
Authorization: Token <token>
X-Session-Id: <session_id>
```

**Request Body:**
```json
{
  "old_password": "OldPass123!",
  "new_password": "NewPass456!",
  "new_password_confirm": "NewPass456!"
}
```

**Success Response — `200 OK`:**
```json
{
  "message": "Password changed successfully."
}
```

---

## 2. Password Reset

Three-step flow: request OTP → (optionally verify OTP) → reset password.

### 2.1 Request Reset OTP

```
POST /api/users/password-reset/request/
```

**Request Body:**
```json
{
  "email": "john@example.com"
}
```

**Response — `200 OK`** (always, even if email not found — for security):
```json
{
  "message": "If an account with this email exists, a password reset code has been sent."
}
```

**Email delivery failure — `500 Internal Server Error`:**
```json
{
  "error": "Failed to send email. Please try again later."
}
```

> ⚠️ The OTP is **not** persisted to the database until the email is confirmed delivered. No dangling tokens.

**Rate limit:** 3 requests/hour per IP.

---

### 2.2 Verify Reset OTP

Optional step to validate the OTP before showing the new-password form.

```
POST /api/users/password-reset/verify-otp/
```

**Request Body:**
```json
{
  "email": "john@example.com",
  "otp": "739201"
}
```

**Success Response — `200 OK`:**
```json
{
  "message": "OTP verified successfully."
}
```

**Failure — `400 Bad Request`:**
```json
{
  "error": "Invalid or expired OTP."
}
```

---

### 2.3 Reset Password

```
POST /api/users/password-reset/reset/
```

**Request Body:**
```json
{
  "email": "john@example.com",
  "otp": "739201",
  "new_password": "NewPass456!",
  "new_password_confirm": "NewPass456!"
}
```

**Success Response — `200 OK`:**
```json
{
  "message": "Password reset successfully. You can now login with your new password."
}
```

**Failure — `400 Bad Request`:**
```json
{
  "error": "Invalid or expired OTP."
}
```

---

## 3. Google OAuth

### Login with Google

```
POST /api/users/auth/google/login/
```

**Request Body:**
```json
{
  "id_token": "<Google ID token from Google Sign-In SDK>"
}
```

**Response — `200 OK`** (same as regular login):
```json
{
  "user": { ... },
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "session_id": "a3f2c1d0-5e6b-4a7c-8d9e-1b2f3c4d5e6f"
}
```

> Same token rotation and session enforcement applies.

---

## 4. Google Play Payments

### 4.1 Verify Purchase

Validates a Google Play subscription purchase token with the Google Play Developer API and grants premium access.

```
POST /api/payments/verify/
Authorization: Token <token>
X-Session-Id: <session_id>
Content-Type: application/json
```

**Request Body:**
```json
{
  "purchase_token": "oiibkfnlkjhdfakjhsdfkj...",
  "product_id": "agames_premium_monthly",
  "package_name": "com.agames.app"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `purchase_token` | string | ✅ | Token from Google Play Billing Library |
| `product_id` | string | ✅ | Subscription product ID (see below) |
| `package_name` | string | ❌ | Defaults to `com.agames.app` |

**Available Product IDs:**
| Product ID | Duration | Description |
|------------|----------|-------------|
| `agames_premium_monthly` | 1 month | Monthly subscription |
| `agames_premium_quarterly` | 3 months | Quarterly subscription |
| `agames_premium_yearly` | 12 months | Annual subscription |

---

**Success Response — `200 OK`:**
```json
{
  "message": "Purchase verified successfully!",
  "is_premium": true,
  "expiration_date": "2026-01-28T14:30:00Z",
  "product_id": "agames_premium_monthly"
}
```

**Token already claimed by same user (idempotent retry) — `200 OK`:**
```json
{
  "message": "Purchase already verified for your account.",
  "is_premium": true,
  "expiration_date": "2026-01-28T14:30:00Z"
}
```

**Token already claimed by a different user (fraud) — `409 Conflict`:**
```json
{
  "error": "This purchase token has already been claimed by another account."
}
```

**Google Play verification failed — `400 Bad Request`:**
```json
{
  "error": "Subscription not found or has expired."
}
```

**Not authenticated — `401 Unauthorized`:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

**How it works:**

1. The mobile app completes a Google Play Billing purchase and receives a `purchaseToken`.
2. The app sends the token to this endpoint.
3. The server calls the **Google Play Developer API** to verify the token is valid and active.
4. **Anti-fraud check:** the token is stored in the database with the user's ID. Any future attempt to use the same token from a different account is rejected with `409`.
5. On success, `user.is_premium = True` and `user.premium_expiration` is set to the subscription expiry from Google.
6. The app should call `GET /api/users/status/` on every startup to keep premium status current (auto-expiry is handled server-side).

---

**Integration Flow (Mobile App):**
```
User taps "Subscribe"
    └→ Google Play Billing Library: launchBillingFlow()
        └→ On purchase success: purchaseToken received
            └→ POST /api/payments/verify/  { purchase_token, product_id }
                └→ 200 OK: show premium content
                └→ 409: show "already claimed" error
                └→ 400: show "verification failed" error
```

---

## 5. Anti-Sharing Enforcement

AGames enforces **single active session** per account to prevent token sharing.

### How it works

1. **Login** generates a new UUID `session_id` and returns it alongside the auth token.
2. Every subsequent request should include:
   ```
   Authorization: Token <token>
   X-Session-Id: <session_id>
   ```
3. If the user logs in from a second device, a **new** `session_id` is generated. The old device's `session_id` no longer matches.
4. The old device's next request returns `401`:
   ```json
   {
     "detail": "Your session has been invalidated because you logged in on another device. Please log in again.",
     "code": "session_invalidated"
   }
   ```

### Backward Compatibility

- If the client does **not** send `X-Session-Id`, the request is allowed through (graceful rollout).
- If the user has no `session_id` in the database yet (legacy accounts), the check is skipped until next login.

### What triggers session rotation?

| Event | Effect |
|-------|--------|
| `POST /api/users/login/` | New token + new `session_id` issued |
| `POST /api/users/logout/` | Token deleted, `session_id` cleared |
| `POST /api/users/auth/google/login/` | New token + new `session_id` issued |

---

## 6. Error Reference

| HTTP Code | Meaning |
|-----------|---------|
| `200 OK` | Success |
| `201 Created` | Resource created |
| `400 Bad Request` | Invalid input or failed validation |
| `401 Unauthorized` | Missing token, invalid token, or session mismatch |
| `403 Forbidden` | Email not verified or permission denied |
| `404 Not Found` | Resource not found |
| `409 Conflict` | Duplicate resource (e.g. purchase token reuse) |
| `429 Too Many Requests` | Rate limit exceeded |
| `500 Internal Server Error` | Server error (e.g. email delivery failure) |

### Rate Limits

| Endpoint Group | Limit |
|----------------|-------|
| `POST /api/users/login/` | 5 requests/5 minutes |
| `POST /api/users/register/` | 5 requests/hour |
| `POST /api/users/resend-otp/` | 3 requests/hour |
| `POST /api/users/password-reset/request/` | 3 requests/hour |

---

## Mail Infrastructure

Transactional emails (OTP, password reset) are sent via the server's own Postfix installation:

- **From:** `noreply@games.agames.cv`
- **DKIM:** Signed with selector `mail` for domain `games.agames.cv`
- **SPF:** `v=spf1 a mx ip4:152.53.206.21 ~all`
- **MX:** `10 games.agames.cv.`

OTP emails are only written to the database **after** successful SMTP delivery. If delivery fails, the endpoint returns `500` — no dangling tokens are stored.
