# AGames — Mobile App Integration Guide

> **Version:** 2.0 · **Updated:** 2026-03-01  
> **Base URL:** `https://games.agames.cv/api/`

---

## Overview of Changes

This document covers the **login system** (with anti-sharing / single-session enforcement) and the **Google Play subscription** flow. All changes are **backward compatible** — the current app will continue working without modifications. New features activate only once the app starts sending the new headers.

---

## Table of Contents

1. [Authentication Flow](#1-authentication-flow)
2. [Anti-Sharing (Single Session)](#2-anti-sharing-single-session)
3. [Google Play Subscription Verification](#3-google-play-subscription-verification)
4. [Premium Status Check](#4-premium-status-check)
5. [Complete Endpoint Reference](#5-complete-endpoint-reference)
6. [Error Handling](#6-error-handling)
7. [Migration Checklist](#7-migration-checklist)

---

## 1. Authentication Flow

### 1.1 Login

```
POST /api/users/login/
Content-Type: application/json
```

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response `200 OK`:**
```json
{
  "user": {
    "id": 5,
    "email": "user@example.com",
    "username": "player1",
    "is_premium": false,
    "is_email_verified": true,
    "profile_picture": null,
    "premium_expiration": null
  },
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "session_id": "a3f2c1d0-5e6b-4a7c-8d9e-1b2f3c4d5e6f"
}
```

> **⚠️ IMPORTANT — Save both `token` and `session_id` locally (e.g. SharedPreferences / UserDefaults). You need both for every subsequent API call.**

### 1.2 Google Login

```
POST /api/users/auth/google/
Content-Type: application/json
```

**Request:**
```json
{
  "id_token": "<Google ID token from Google Sign-In SDK>"
}
```

**Response `200 OK`:** same structure as regular login (includes `token`, `session_id`, `user`).

### 1.3 Logout

```
POST /api/users/logout/
Authorization: Token <token>
X-Session-Id: <session_id>
```

**Response `200 OK`:**
```json
{
  "message": "Successfully logged out."
}
```

---

## 2. Anti-Sharing (Single Session)

### How It Works

Only **one active session** is allowed per account. When a user logs in on a new device, the previous device's session is invalidated.

### What the App Must Do

**Step 1 — Send two headers on EVERY authenticated request:**
```
Authorization: Token <token>
X-Session-Id: <session_id>
```

**Step 2 — Handle the `session_invalidated` error:**

When the server detects the session was invalidated (user logged in on another device), the response will be:

```
HTTP/1.1 401 Unauthorized
Content-Type: application/json
```
```json
{
  "detail": "Your session has been invalidated because you logged in on another device. Please log in again.",
  "code": "session_invalidated"
}
```

**Step 3 — In the app, check for this response:**

```
IF response.status == 401 AND response.body.code == "session_invalidated":
    → Clear stored token and session_id
    → Navigate to Login screen
    → Show message: "You have been logged out because your account was used on another device."
```

### Flow Diagram

```
Device A logs in
  → receives token + session_id_A
  → stores both locally
  → sends both on every request ✅

            Device B logs in (same account)
              → receives SAME token + session_id_B (new)
              → session_id_A is now invalid on server

Device A makes any API request
  → sends token + session_id_A
  → Server: token valid, but session_id_A ≠ session_id_B
  → Response: 401 { "code": "session_invalidated" }
  → App: redirect to login screen
```

### Backward Compatibility

| Scenario | Behavior |
|----------|----------|
| App does NOT send `X-Session-Id` header | Session check is **skipped**. App works normally. |
| App sends `X-Session-Id` header | Session enforcement is **active**. |
| User account has no session_id yet (old user) | Session check is **skipped** until next login. |

> This means the current app version will keep working. Enforcement only starts once the app is updated to send `X-Session-Id`.

---

## 3. Google Play Subscription Verification

After a successful Google Play purchase, the app must send the purchase token to the server for verification.

### 3.1 Verify Purchase

```
POST /api/payments/verify/
Authorization: Token <token>
X-Session-Id: <session_id>
Content-Type: application/json
```

**Request:**
```json
{
  "purchase_token": "oiibkfnlkjhdfakjhsdfkjahsdfjkhaskdjfh...",
  "product_id": "agames_sub_1month"
}
```

**Available Product IDs:**

| Product ID | Duration | Description |
|------------|----------|-------------|
| `agames_sub_1month` | 30 days | AGames Monthly Pass |
| `agames_sub_3months` | 90 days | AGames Quarter Pass |
| `agames_sub_6months` | 180 days | AGames Semi-Annual Pass |

> The `product_id` must match exactly one of the above values.

**Success Response `200 OK`:**
```json
{
  "message": "Purchase verified successfully!",
  "is_premium": true,
  "expiration_date": "2026-04-01T14:30:00Z",
  "product_id": "agames_sub_1month"
}
```

**Already verified (same user, same token — safe retry) `200 OK`:**
```json
{
  "message": "Purchase already verified for your account.",
  "is_premium": true,
  "expiration_date": "2026-04-01T14:30:00Z"
}
```

**Token already claimed by another user (fraud attempt) `409 Conflict`:**
```json
{
  "error": "This purchase token has already been claimed by another account."
}
```

**Google Play verification failed `400 Bad Request`:**
```json
{
  "error": "Google Play verification failed."
}
```

### Integration Flow (Kotlin/Java Example)

```kotlin
// 1. Complete Google Play purchase
billingClient.launchBillingFlow(activity, flowParams)

// 2. On purchase success
override fun onPurchasesUpdated(result: BillingResult, purchases: List<Purchase>?) {
    if (result.responseCode == OK && purchases != null) {
        for (purchase in purchases) {
            verifyOnServer(purchase.purchaseToken, purchase.products[0])
        }
    }
}

// 3. Send to your server
fun verifyOnServer(purchaseToken: String, productId: String) {
    val body = mapOf(
        "purchase_token" to purchaseToken,
        "product_id" to productId
    )
    api.post("/api/payments/verify/", body, headers = mapOf(
        "Authorization" to "Token $savedToken",
        "X-Session-Id" to "$savedSessionId"
    ))
    // On 200: user is now premium
    // On 409: token was already used by another account
    // On 401 + code=session_invalidated: redirect to login
}

// 4. After successful verification, acknowledge the purchase
billingClient.acknowledgePurchase(
    AcknowledgePurchaseParams.newBuilder()
        .setPurchaseToken(purchaseToken)
        .build()
)
```

---

## 4. Premium Status Check

Call this endpoint every time the app starts or comes back to foreground to keep premium status in sync.

```
GET /api/users/status/
Authorization: Token <token>
X-Session-Id: <session_id>
```

**Response `200 OK`:**
```json
{
  "is_premium": true,
  "expiration_date": "2026-04-01T14:30:00Z",
  "email": "user@example.com",
  "username": "player1"
}
```

```json
{
  "is_premium": false,
  "expiration_date": null,
  "email": "user@example.com",
  "username": "player1"
}
```

> The server automatically expires premium when the date passes. Always trust this endpoint over local state.

---

## 5. Complete Endpoint Reference

### Authentication Endpoints (no auth required)

| Method | URL | Description |
|--------|-----|-------------|
| `POST` | `/api/users/register/` | Create account (sends OTP email) |
| `POST` | `/api/users/verify-otp/` | Verify email with 6-digit OTP |
| `POST` | `/api/users/resend-otp/` | Resend verification OTP |
| `POST` | `/api/users/login/` | Email/password login → returns `token` + `session_id` |
| `POST` | `/api/users/auth/google/` | Google ID token login → returns `token` + `session_id` |
| `POST` | `/api/users/password-reset/request/` | Request password reset OTP |
| `POST` | `/api/users/password-reset/verify-otp/` | Verify reset OTP |
| `POST` | `/api/users/password-reset/reset/` | Reset password with OTP |

### Authenticated Endpoints (require `Authorization` + `X-Session-Id`)

| Method | URL | Description |
|--------|-----|-------------|
| `POST` | `/api/users/logout/` | Logout (clears session) |
| `GET` | `/api/users/status/` | Premium status check (call on app start) |
| `GET` | `/api/users/profile/` | Get profile |
| `PATCH` | `/api/users/profile/` | Update profile |
| `POST` | `/api/users/profile/picture/` | Upload profile picture (multipart) |
| `POST` | `/api/users/change-password/` | Change password (requires old password) |
| `POST` | `/api/payments/verify/` | Verify Google Play purchase token |

### Request Headers

```
# Required for ALL authenticated endpoints:
Authorization: Token <token>
X-Session-Id: <session_id>

# For JSON body requests:
Content-Type: application/json

# For file uploads:
Content-Type: multipart/form-data
```

---

## 6. Error Handling

### HTTP Status Codes

| Code | Meaning | App Action |
|------|---------|------------|
| `200` | Success | Process response |
| `201` | Created | Process response |
| `400` | Bad request / validation error | Show error message from response |
| `401` | Unauthorized | **Check `code` field (see below)** |
| `403` | Email not verified | Navigate to email verification screen |
| `404` | Resource not found | Show "not found" |
| `409` | Conflict (e.g. duplicate purchase token) | Show specific error |
| `429` | Rate limited | Show "try again later" |
| `500` | Server error | Show "server error, try again" |

### Handling 401 Responses

Every `401` response should be checked for the `code` field:

```json
// Case 1: Session invalidated (logged in on another device)
{
  "detail": "Your session has been invalidated because you logged in on another device. Please log in again.",
  "code": "session_invalidated"
}
→ Clear token + session_id → Navigate to Login → Show "logged in on another device" message

// Case 2: Generic invalid/expired token
{
  "detail": "Invalid token."
}
→ Clear token + session_id → Navigate to Login

// Case 3: Token not provided
{
  "detail": "Authentication credentials were not provided."
}
→ Navigate to Login
```

**Recommended global interceptor (pseudo-code):**
```
ON EVERY API RESPONSE:
    IF status == 401:
        IF body.code == "session_invalidated":
            showDialog("Your account is being used on another device. Please log in again.")
        clearStoredCredentials()
        navigateToLogin()
```

### Rate Limits

| Endpoint | Limit |
|----------|-------|
| Login | 5 requests / minute |
| OTP / Resend | 2 requests / minute |
| Authenticated endpoints | 100 requests / minute |
| Anonymous endpoints | 50 requests / minute |

---

## 7. Migration Checklist

### Phase 1: Add X-Session-Id Support (Non-Breaking)

- [ ] On login success, **save `session_id`** from the response alongside the token
- [ ] Add `X-Session-Id: <session_id>` header to **all** authenticated API calls
- [ ] Add global 401 handler: check for `"code": "session_invalidated"` → redirect to login with message
- [ ] Handle generic 401 (no code) → redirect to login

### Phase 2: Add Google Play Subscription

- [ ] After Google Play purchase success, call `POST /api/payments/verify/` with `purchase_token` + `product_id`
- [ ] Handle `200` → update local premium state
- [ ] Handle `409` → show "token already claimed" error
- [ ] Handle `400` → show "verification failed" error
- [ ] On app start / resume, call `GET /api/users/status/` → sync premium state
- [ ] Use `is_premium` and `expiration_date` from response to gate premium content

### Phase 3: Testing

- [ ] Login on Device A → verify `token` and `session_id` are received
- [ ] Login on Device B (same account) → verify new `session_id` received
- [ ] Make any API call from Device A with `X-Session-Id` header → verify 401 with `"code": "session_invalidated"`
- [ ] Verify Device A redirects to login screen with appropriate message
- [ ] Test Google Play purchase → verify call → verify premium status updates
- [ ] Test app restart → verify `GET /api/users/status/` returns correct premium state
- [ ] Test without `X-Session-Id` header → verify requests still work (backward compat)

---

## Quick Reference Card

```
┌────────────────────────────────────────────────────────────┐
│                    AGames API Quick Ref                     │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  LOGIN:  POST /api/users/login/                            │
│  GOOGLE: POST /api/users/auth/google/                      │
│          → Save: token + session_id                        │
│                                                            │
│  HEADERS (every authenticated request):                    │
│    Authorization: Token <token>                            │
│    X-Session-Id: <session_id>                              │
│                                                            │
│  PREMIUM CHECK: GET /api/users/status/                     │
│          → Use is_premium + expiration_date                │
│                                                            │
│  VERIFY PURCHASE: POST /api/payments/verify/               │
│    { "purchase_token": "...", "product_id": "..." }        │
│                                                            │
│  PRODUCT IDs:                                              │
│    agames_sub_1month   (30 days)                           │
│    agames_sub_3months  (90 days)                           │
│    agames_sub_6months  (180 days)                          │
│                                                            │
│  SESSION KICKED → 401 { "code": "session_invalidated" }   │
│    → Clear credentials → Go to Login screen                │
│                                                            │
└────────────────────────────────────────────────────────────┘
```
