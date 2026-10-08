# AGames API - Complete Reference

**Base URL:** `http://localhost:8000/api/`

**Last Updated:** November 18, 2025

---

## 🆕 Recent Changes (v2.0)

### Major Updates:
- ✅ **Removed Genre Field**: Games now use flexible **tags** instead of fixed genre choices
- ✅ **URL-Based Images**: `cover_image` and `icon` are now URL fields (CDN-ready, no file uploads)
- ✅ **Enhanced Filtering**: Filter by `emulator`, `is_premium`, and search by `tags`
- ✅ **Database Optimized**: 40+ indexes for 50-70% faster queries
- ✅ **Download Simplified**: Frontend handles progress, backend tracks history only
- ✅ **Separate Reviews**: Unlimited reviews per user, separate from ratings

---

## Table of Contents
1. [Authentication](#authentication)
2. [Users Management](#users-management)
3. [Games & Emulators](#games--emulators)
4. [Subscriptions](#subscriptions)
5. [Payments](#payments)
6. [Common Headers](#common-headers)
7. [Error Responses](#error-responses)
8. [Quick Reference](#quick-reference)

---

## Quick Reference

### Users Management Endpoints (13 endpoints)

| # | Endpoint | Method | Auth Required | Purpose |
|---|----------|--------|---------------|---------|
| 1.1 | `/api/users/register/` | POST | ❌ No | Register new user |
| 1.2 | `/api/users/verify-otp/` | POST | ❌ No | Verify email with OTP |
| 1.3 | `/api/users/resend-otp/` | POST | ❌ No | Resend verification OTP |
| 1.4 | `/api/users/login/` | POST | ❌ No | Login with email/password |
| 1.5 | `/api/users/auth/google/` | POST | ❌ No | Login with Google OAuth |
| 1.6 | `/api/users/logout/` | POST | ✅ Yes | Logout user |
| 1.7 | `/api/users/profile/` | GET | ✅ Yes | Get user profile |
| 1.8 | `/api/users/profile/` | PUT | ✅ Yes | Update user profile |
| 1.9 | `/api/users/change-password/` | POST | ✅ Yes | Change password (requires old password) |
| 1.10 | `/api/users/password-reset/request/` | POST | ❌ No | Request password reset OTP |
| 1.11 | `/api/users/password-reset/verify-otp/` | POST | ❌ No | Verify password reset OTP |
| 1.12 | `/api/users/password-reset/reset/` | POST | ❌ No | Reset password with OTP |
| 1.13 | `/api/users/admin/update-premium/` | PATCH | ✅ Yes (Admin) | Update user premium status |

### Games & Emulators Endpoints (17 endpoints)

| Endpoint | Method | Auth Required | Purpose |
|----------|--------|---------------|---------|
| `/api/emulators/` | GET | ❌ No | List all emulators |
| `/api/emulators/{id}/` | GET | ❌ No | Get emulator details |
| `/api/games/` | GET | ❌ No | List all games |
| `/api/games/{id}/` | GET | ❌ No | Get game details |
| `/api/games/{id}/download/` | POST | ✅ Yes | Download game |
| `/api/games/{id}/rate/` | POST | ✅ Yes | Rate game (1.0-5.0 in 0.5 increments, one per user) |
| `/api/games/{id}/ratings/` | GET | ❌ No | Get game ratings |
| `/api/games/{id}/add_review/` | POST | ✅ Yes | Add review (unlimited reviews per user) |
| `/api/games/{id}/reviews/` | GET | ❌ No | Get game reviews |
| `/api/games/my_reviews/` | GET | ✅ Yes | Get my reviews |
| `/api/games/{id}/love/` | POST | ✅ Yes | Love/unlike game (toggle) |
| `/api/games/my_loved_games/` | GET | ✅ Yes | Get my loved games |
| `/api/games/my_downloads/` | GET | ✅ Yes | Get user's downloads |
| `/api/games/{id}/delete_download/` | DELETE | ✅ Yes | Delete download |

### Subscriptions Endpoints (6 endpoints)

| Endpoint | Method | Auth Required | Purpose |
|----------|--------|---------------|---------|
| `/api/subscriptions/plans/` | GET | ❌ No | List subscription plans |
| `/api/subscriptions/plans/{id}/` | GET | ❌ No | Get plan details |
| `/api/subscriptions/subscriptions/` | POST | ✅ Yes | Create subscription |
| `/api/subscriptions/subscriptions/` | GET | ✅ Yes | List my subscriptions |
| `/api/subscriptions/subscriptions/{id}/` | GET | ✅ Yes | Get subscription details |
| `/api/subscriptions/subscriptions/{id}/` | PATCH | ✅ Yes | Cancel subscription |

### Payments Endpoints (4 endpoints)

| Endpoint | Method | Auth Required | Purpose |
|----------|--------|---------------|---------|
| `/api/payments/create-payment-intent/` | POST | ✅ Yes | Create Stripe payment intent |
| `/api/payments/payments/` | GET | ✅ Yes | List payment history |
| `/api/payments/payments/{id}/` | GET | ✅ Yes | Get payment details |
| `/api/payments/webhook/stripe/` | POST | ❌ No* | Stripe webhook (*uses signature) |

**Total: 35+ API Endpoints**

---

## Authentication

All authenticated endpoints require a token in the Authorization header:
```
Authorization: Token <your-token-here>
```

---

# 1. USERS MANAGEMENT

## 1.1 Register User

**Endpoint:** `POST /api/users/register/`

**Authentication:** Not required

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "username": "johndoe"
}
```

**Required Fields:**
- `email` (string, unique)
- `password` (string, min 8 chars)
- `password_confirm` (string, must match password)

**Optional Fields:**
- `first_name` (string)
- `last_name` (string)
- `username` (string, auto-generated from email if not provided)

**Success Response (201 Created):**
```json
{
  "message": "User registered successfully. Please verify your email.",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe",
    "is_premium": false,
    "is_email_verified": false,
    "created_at": "2025-11-16T10:30:00Z"
  }
}
```

**Email Sent:**
- Subject: "Your Verification Code - AGames"
- Contains 6-digit OTP code
- Valid for 10 minutes

**Error Responses:**
```json
// 400 Bad Request - Email already exists
{
  "email": ["User with this email already exists."]
}

// 400 Bad Request - Password mismatch
{
  "password_confirm": ["Passwords do not match."]
}

// 400 Bad Request - Weak password
{
  "password": ["This password is too common."]
}
```

---

## 1.2 Verify Email (OTP)

**Endpoint:** `POST /api/users/verify-otp/`

**Authentication:** Not required

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "otp": "123456"
}
```

**Required Fields:**
- `email` (string)
- `otp` (string, 6 digits)

**Success Response (200 OK):**
```json
{
  "message": "Email verified successfully",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "is_email_verified": true
  },
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
}
```

**Error Responses:**
```json
// 400 Bad Request - Invalid OTP
{
  "error": "Invalid or expired OTP"
}

// 400 Bad Request - User not found
{
  "error": "User not found"
}

// 400 Bad Request - Already verified
{
  "error": "Email already verified"
}
```

---

## 1.3 Resend OTP

**Endpoint:** `POST /api/users/resend-otp/`

**Authentication:** Not required

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Success Response (200 OK):**
```json
{
  "message": "Verification code sent to your email"
}
```

**Rate Limiting:**
- Maximum 3 OTP requests per 15 minutes per email

**Error Responses:**
```json
// 400 Bad Request - Already verified
{
  "error": "Email already verified"
}

// 429 Too Many Requests - Rate limit exceeded
{
  "error": "Too many OTP requests. Please wait before requesting again."
}
```

---

## 1.4 Login

**Endpoint:** `POST /api/users/login/`

**Authentication:** Not required

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Required Fields:**
- `email` (string)
- `password` (string)

**Success Response (200 OK):**
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe",
    "profile_picture": null,
    "is_premium": false,
    "is_email_verified": true,
    "created_at": "2025-11-16T10:30:00Z"
  },
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
}
```

**Error Responses:**
```json
// 400 Bad Request - Invalid credentials
{
  "error": "Invalid email or password"
}

// 400 Bad Request - Email not verified
{
  "error": "Please verify your email before logging in"
}
```

---

## 1.5 Google Sign-In

**Endpoint:** `POST /api/users/auth/google/`

**Authentication:** Not required

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjE5ZDhjNz..."
}
```

**Required Fields:**
- `id_token` (string, Google ID token from Google Sign-In SDK)

**Success Response (200 OK):**
```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "email": "user@gmail.com",
    "username": "John Doe",
    "profile_picture": "https://lh3.googleusercontent.com/...",
    "is_premium": false,
    "is_email_verified": true,
    "created_at": "2025-11-16T10:30:00Z"
  },
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "is_new_user": false
}
```

**Response Fields:**
- `is_new_user` (boolean): `true` if account was just created, `false` if existing user

**Error Responses:**
```json
// 400 Bad Request - Invalid token
{
  "error": "Invalid Google token"
}

// 400 Bad Request - Email not provided
{
  "error": "Email not provided by Google"
}
```

---

## 1.6 Logout

**Endpoint:** `POST /api/users/logout/`

**Authentication:** Required

**Request Headers:**
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
Content-Type: application/json
```

**Request Body:** None

**Success Response (200 OK):**
```json
{
  "message": "Successfully logged out"
}
```

---

## 1.7 Get Profile

**Endpoint:** `GET /api/users/profile/`

**Authentication:** Required

**Request Headers:**
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

**Success Response (200 OK):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "first_name": "John",
  "last_name": "Doe",
  "profile_picture": null,
  "is_premium": false,
  "is_email_verified": true,
  "created_at": "2025-11-16T10:30:00Z"
}
```

---

## 1.8 Update Profile

**Endpoint:** `PUT /api/users/profile/`

**Authentication:** Required

**Request Headers:**
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
Content-Type: application/json
```

**Request Body:**
```json
{
  "first_name": "Jane",
  "last_name": "Smith",
  "username": "janesmith"
}
```

**Updatable Fields:**
- `first_name` (string)
- `last_name` (string)
- `username` (string, unique)
- `profile_picture` (file upload in multipart/form-data)

**Success Response (200 OK):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "janesmith",
  "first_name": "Jane",
  "last_name": "Smith",
  "profile_picture": null,
  "is_premium": false,
  "is_email_verified": true,
  "created_at": "2025-11-16T10:30:00Z"
}
```

**Note:** To upload profile picture, use `multipart/form-data`:
```
Content-Type: multipart/form-data
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b

--boundary
Content-Disposition: form-data; name="profile_picture"; filename="photo.jpg"
Content-Type: image/jpeg

<binary image data>
--boundary--
```

---

## 1.9 Change Password (Logged In)

**Endpoint:** `POST /api/users/change-password/`

**Authentication:** Required

**Request Headers:**
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
Content-Type: application/json
```

**Request Body:**
```json
{
  "old_password": "OldPassword123!",
  "new_password": "NewSecurePass456!",
  "confirm_password": "NewSecurePass456!"
}
```

**Required Fields:**
- `old_password` (string, min 8 chars)
- `new_password` (string, min 8 chars)
- `confirm_password` (string, must match new_password)

**Success Response (200 OK):**
```json
{
  "message": "Password changed successfully. Please use your new password for future logins.",
  "token": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0"
}
```

**Note:** A new token is issued after password change. Old token is invalidated.

**Error Responses:**
```json
// 400 Bad Request - Incorrect old password
{
  "error": "Old password is incorrect."
}

// 400 Bad Request - Passwords don't match
{
  "new_password": ["New passwords do not match"]
}

// 400 Bad Request - Same password
{
  "non_field_errors": ["New password must be different from old password"]
}

// 401 Unauthorized - Not logged in
{
  "detail": "Authentication credentials were not provided."
}
```

---

## 1.10 Request Password Reset (Forgot Password)

**Endpoint:** `POST /api/users/password-reset/request/`

**Authentication:** Not required

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Success Response (200 OK):**
```json
{
  "message": "If an account with this email exists, a password reset code has been sent."
}
```

**Email Sent:**
- Subject: "Password Reset Code - AGames"
- Contains 6-digit OTP code
- Valid for 10 minutes

**Error Responses:**
```json
// 400 Bad Request - User not found (message is generic for security)
{
  "message": "If an account with this email exists, a password reset code has been sent."
}
```

**Email Sent:**
- Subject: "Password Reset Code - AGames"
- Contains 6-digit OTP code
- Valid for 10 minutes

**Error Responses:**
```json
// 400 Bad Request - User not found (message is generic for security)
{
  "message": "If an account with this email exists, a password reset code has been sent."
}
```

---

## 1.11 Verify Password Reset OTP (Forgot Password)

**Endpoint:** `POST /api/users/password-reset/verify-otp/`

**Authentication:** Not required

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "otp": "123456"
}
```

**Success Response (200 OK):**
```json
{
  "message": "OTP verified successfully. You can now reset your password."
}
```

**Error Responses:**
```json
// 400 Bad Request - Invalid OTP
{
  "error": "Invalid or expired OTP"
}
```

---

## 1.12 Reset Password (Forgot Password)

**Endpoint:** `POST /api/users/password-reset/reset/`

**Authentication:** Not required

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "otp": "123456",
  "new_password": "NewSecurePass123!",
  "confirm_password ": "NewSecurePass123!"
}
```

**Required Fields:**
- `email` (string)
- `otp` (string, 6 digits)
- `new_password` (string, min 8 chars)
- `confirm_password` (string, must match new_password)

**Success Response (200 OK):**
```json
{
  "message": "Password reset successfully"
}
```

**Error Responses:**
```json
// 400 Bad Request - Invalid OTP
{
  "error": "Invalid or expired OTP"
}

// 400 Bad Request - Password mismatch
{
  "error": "Passwords do not match"
}
```

---

## 1.13 Update Premium Status (Admin Only)

**Endpoint:** `PATCH /api/users/admin/update-premium/`

**Authentication:** Required (Superuser only)

**Request Headers:**
```
Authorization: Token <superuser-token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "user_id": 1,
  "is_premium": true
}
```

**Success Response (200 OK):**
```json
{
  "message": "Premium status updated successfully",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "is_premium": true
  }
}
```

**Error Responses:**
```json
// 403 Forbidden - Not admin
{
  "detail": "You do not have permission to perform this action."
}

// 404 Not Found - User not found
{
  "error": "User not found"
}
```

---

# 2. GAMES & EMULATORS

## 2.1 List Emulators

**Endpoint:** `GET /api/games/emulators/`

**Authentication:** Not required

**Request Headers:**
```
Content-Type: application/json
```

**Query Parameters:**
- `search` (string, optional): Search by name
- `ordering` (string, optional): Order by field (e.g., `name`, `-name`)

**Example Request:**
```
GET /api/games/emulators/?search=PS2&ordering=name
```

**Success Response (200 OK):**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "PlayStation 2",
      "icon": "https://cdn.example.com/ps2-icon.png",
      "description": "Sony PlayStation 2 emulator"
    },
    {
      "id": 2,
      "name": "Nintendo 64",
      "icon": "https://cdn.example.com/n64-icon.png",
      "description": "Nintendo 64 emulator"
    }
  ]
}
```

---

## 2.2 Get Emulator Details

**Endpoint:** `GET /api/games/emulators/{id}/`

**Authentication:** Not required

**Request Headers:**
```
Content-Type: application/json
```

**Success Response (200 OK):**
```json
{
  "id": 1,
  "name": "PlayStation 2",
  "icon": "https://cdn.example.com/ps2-icon.png",
  "description": "Sony PlayStation 2 emulator"
}
```

---

## 2.3 List Games

**Endpoint:** `GET /api/games/`

**Authentication:** Not required

**Request Headers:**
```
Content-Type: application/json
```

**Query Parameters:**
- `search` (string, optional): Search by title, description, or tag name
- `emulator` (integer, optional): Filter by emulator ID
- `tags` (string, optional): Filter by tag name
- `is_premium` (boolean, optional): Filter by premium status (true/false)
- `ordering` (string, optional): Order by field (e.g., `title`, `-created_at`, `release_date`)
- `page` (integer, optional): Page number
- `page_size` (integer, optional): Items per page (default: 20, max: 50)

**Example Request:**
```
GET /api/games/?emulator=1&is_premium=false&ordering=-created_at&page=1&search=zelda
```

**Success Response (200 OK):**
```json
{
  "count": 50,
  "next": "http://localhost:8000/api/games/games/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "God of War",
      "cover_image": "https://cdn.example.com/gow-cover.jpg",
      "average_rating": 4.8,
      "total_loves": 342,
      "total_downloads": 1542
    },
    {
      "id": 2,
      "title": "Grand Theft Auto: San Andreas",
      "cover_image": "https://cdn.example.com/gta-sa-cover.jpg",
      "average_rating": 4.9,
      "total_loves": 458,
      "total_downloads": 2103
    }
  ]
}
```

---

## 2.4 Get Game Details

**Endpoint:** `GET /api/games/{id}/`

**Authentication:** Not required

**Request Headers:**
```
Content-Type: application/json
```

**Success Response (200 OK):**
```json
{
  "id": 51,
  "title": "The Legend of Zelda",
  "description": "An epic action-adventure game featuring Link...",
  "cover_image": "https://cdn.example.com/zelda-cover.jpg",
  "emulator": {
    "id": 1,
    "name": "Nintendo 64",
    "icon": "https://cdn.example.com/n64-icon.png",
    "description": "Nintendo 64 Emulator"
  },
  "file_size": "32 MB",
  "download_url": "https://example.com/games/zelda.zip",
  "tags": [
    {"id": 1, "name": "Action"},
    {"id": 2, "name": "Adventure"},
    {"id": 3, "name": "RPG"}
  ],
  "is_premium": false,
  "release_date": "1998-11-21",
  "created_at": "2025-11-15T10:00:00Z",
  "updated_at": "2025-11-18T08:30:00Z",
  "average_rating": 4.5,
  "total_downloads": 15420,
  "total_loves": 8932
}
```

**Note:** Authentication adds additional user-specific fields when logged in.

---

## 2.5 Download Game

**Endpoint:** `POST /api/games/{id}/download/`

**Authentication:** Required

**Request Headers:**
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
Content-Type: application/json
```

**Request Body:** None

**Success Response (201 Created):**
```json
{
  "id": 1,
  "game": {
    "id": 1,
    "title": "God of War"
  },
  "user": 1,
  "downloaded_at": "2025-11-16T10:30:00Z",
  "download_url": "https://example.com/games/god-of-war.zip"
}
```

**Note:** The frontend handles download progress tracking. The backend only records that a download was initiated.

---

## 2.6 Rate Game

**Endpoint:** `POST /api/games/{id}/rate/`

**Authentication:** Required

**Request Headers:**
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
Content-Type: application/json
```

**Request Body:**
```json
{
  "score": 4.5,
}
```

**Required Fields:**
- `score` (decimal, 1.0 to 5.0 in 0.5 increments)
  - Valid values: `1.0`, `1.5`, `2.0`, `2.5`, `3.0`, `3.5`, `4.0`, `4.5`, `5.0`

**Optional Fields:**
- `review` (string)

**Success Response (201 Created):**
```json
{
  "id": 1,
  "user": 1,
  "user_email": "johndoe@example.com",
  "game": 51,
  "game_title": "The Legend of Zelda",
  "score": 4.5,
  "created_at": "2025-11-18T10:30:00Z"
}
```

**Error Responses:**
```json
// 400 Bad Request - Score is required
{
  "error": "Score is required"
}

// 400 Bad Request - Invalid score range
{
  "error": "Score must be between 1 and 5"
}

// 400 Bad Request - Invalid increment
{
  "error": "Score must be in 0.5 increments (e.g., 1.0, 1.5, 2.0)"
}

// 400 Bad Request - Invalid number
{
  "error": "Score must be a valid number"
}
```

**Note:** If user already has a rating for this game, it will be updated with the new score.

---

## 2.7 Get Game Ratings

**Endpoint:** `GET /api/games/{id}/ratings/`

**Authentication:** Not required

**Request Headers:**
```
Content-Type: application/json
```

**Query Parameters:**
- `page` (integer, optional): Page number
- `page_size` (integer, optional): Items per page

**Success Response (200 OK):**
```json
{
  "count": 150,
  "next": "http://localhost:8000/api/games/51/ratings/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "user": 1,
      "user_email": "user@example.com",
      "game": 51,
      "game_title": "The Legend of Zelda",
      "score": 4.5,
      "created_at": "2025-11-18T10:00:00Z",
      "updated_at": "2025-11-18T10:00:00Z"
    },
    {
      "id": 2,
      "user": 2,
      "user_email": "user2@example.com",
      "game": 51,
      "game_title": "The Legend of Zelda",
      "score": 5.0,
      "created_at": "2025-11-18T09:30:00Z",
      "updated_at": "2025-11-18T09:30:00Z"
    }
  ]
}
```

---

## 2.8 Add Review

**Endpoint:** `POST /api/games/{id}/add_review/`

**Authentication:** Required

**Request Headers:**
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
Content-Type: application/json
```

**Request Body:**
```json
{
  "review": "This game is absolutely amazing! The graphics are stunning, the gameplay is smooth, and the story keeps you engaged for hours. Highly recommended for any RPG fan!"
}
```

**Required Fields:**
- `review` (string, any length)

**Success Response (201 Created):**
```json
{
  "message": "Review added successfully",
  "review": {
    "id": 1,
    "user": 1,
    "user_email": "user@example.com",
    "game": 51,
    "game_title": "The Legend of Zelda",
    "review": "This game is absolutely amazing! The graphics are stunning, the gameplay is smooth, and the story keeps you engaged for hours. Highly recommended for any RPG fan!",
    "created_at": "2025-11-18T10:30:00Z",
    "updated_at": "2025-11-18T10:30:00Z"
  }
}
```

**Error Responses:**
```json
// 400 Bad Request - Review is required
{
  "error": "Review text is required"
}

// 401 Unauthorized
{
  "detail": "Authentication credentials were not provided."
}
```

**Note:** Users can add unlimited reviews for the same game. Each review is saved separately. Reviews can be any length.

---

## 2.9 Get Game Reviews

**Endpoint:** `GET /api/games/{id}/reviews/`

**Authentication:** Not required

**Request Headers:**
```
Content-Type: application/json
```

**Query Parameters:**
- `page` (integer, optional): Page number
- `page_size` (integer, optional): Items per page

**Success Response (200 OK):**
```json
{
  "count": 320,
  "next": "http://localhost:8000/api/games/51/reviews/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "user": 1,
      "user_email": "user@example.com",
      "game": 51,
      "game_title": "The Legend of Zelda",
      "review": "This game is absolutely amazing! The graphics are stunning...",
      "created_at": "2025-11-18T10:30:00Z",
      "updated_at": "2025-11-18T10:30:00Z"
    },
    {
      "id": 2,
      "user": 1,
      "user_email": "user@example.com",
      "game": 51,
      "game_title": "The Legend of Zelda",
      "review": "Update: After 20 hours of gameplay, still loving it! Just discovered a hidden temple.",
      "created_at": "2025-11-18T15:00:00Z",
      "updated_at": "2025-11-18T15:00:00Z"
    }
  ]
}
```

**Note:** Returns all reviews from all users for the specified game, ordered by most recent first.

---

## 2.10 Get My Reviews

**Endpoint:** `GET /api/games/my_reviews/`

**Authentication:** Required

**Request Headers:**
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
Content-Type: application/json
```

**Query Parameters:**
- `page` (integer, optional): Page number
- `page_size` (integer, optional): Items per page

**Success Response (200 OK):**
```json
{
  "count": 15,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "user": 1,
      "user_email": "user@example.com",
      "game": 51,
      "game_title": "The Legend of Zelda",
      "review": "This game is absolutely amazing!...",
      "created_at": "2025-11-18T10:30:00Z",
      "updated_at": "2025-11-18T10:30:00Z"
    },
    {
      "id": 5,
      "user": 1,
      "user_email": "user@example.com",
      "game": 52,
      "game_title": "Super Mario 64",
      "review": "Classic game that never gets old...",
      "created_at": "2025-11-17T14:20:00Z",
      "updated_at": "2025-11-17T14:20:00Z"
    }
  ]
}
```

**Error Responses:**
```json
// 401 Unauthorized
{
  "detail": "Authentication credentials were not provided."
}
```

**Note:** Returns all reviews written by the authenticated user across all games.

---

## 2.11 Love/Unlike Game

**Endpoint:** `POST /api/games/{id}/love/`

**Authentication:** Required

**Description:** Toggle love status for a game. If the game is not loved, it will be added to loved games. If already loved, it will be removed.

**Request Headers:**
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
Content-Type: application/json
```

**Request Body:** None (empty)

**Success Response - Game Loved (201 Created):**
```json
{
  "message": "Game added to loved games",
  "is_loved": true
}
```

**Success Response - Game Unloved (200 OK):**
```json
{
  "message": "Game removed from loved games",
  "is_loved": false
}
```

**Error Responses:**
```json
// 401 Unauthorized
{
  "detail": "Authentication credentials were not provided."
}

// 404 Not Found
{
  "detail": "Game not found."
}
```

**Note:** This endpoint acts as a toggle. Each call switches the love status.

---

## 2.12 Get My Loved Games

**Endpoint:** `GET /api/games/my_loved_games/`

**Authentication:** Required

**Description:** Retrieve all games that the authenticated user has marked as loved.

**Request Headers:**
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
Content-Type: application/json
```

**Query Parameters:**
- `page` (integer, optional): Page number
- `page_size` (integer, optional): Items per page (default: 10)

**Success Response (200 OK):**
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/games/my_loved_games/?page=2",
  "previous": null,
  "results": [
    {
      "id": 51,
      "title": "The Legend of Zelda",
      "cover_image": "https://cdn.example.com/zelda-cover.jpg",
      "average_rating": 4.5,
      "total_loves": 8932,
      "total_downloads": 15420
    }
  ]
}
```

**Error Responses:**
```json
// 401 Unauthorized
{
  "detail": "Authentication credentials were not provided."
}
```

**Note:** Returns only games that are currently loved by the user, ordered by most recently loved first.

---

## 2.13 Get My Downloads

**Endpoint:** `GET /api/games/my_downloads/`

**Authentication:** Required

**Request Headers:**
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
Content-Type: application/json
```

**Query Parameters:**
- `page` (integer, optional): Page number
- `page_size` (integer, optional): Items per page (default: 20, max: 50)

**Success Response (200 OK):**
```json
{
  "count": 15,
  "next": "http://localhost:8000/api/games/my_downloads/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "user": 1,
      "user_email": "user@example.com",
      "game": 51,
      "game_title": "God of War",
      "game_cover": "https://cdn.example.com/gow-cover.jpg",
      "file_size": "45 MB",
      "downloaded_at": "2025-11-16T10:30:00Z",
      "ip_address": "192.168.1.100"
    },
    {
      "id": 2,
      "user": 1,
      "user_email": "user@example.com",
      "game": 23,
      "game_title": "The Legend of Zelda",
      "game_cover": "https://cdn.example.com/zelda-cover.jpg",
      "file_size": "32 MB",
      "downloaded_at": "2025-11-15T14:20:00Z",
      "ip_address": "192.168.1.100"
    }
  ]
}
```

**Note:** Frontend handles download progress tracking. Backend only records download history.

---

## 2.14 Delete Download

**Endpoint:** `DELETE /api/games/{id}/delete_download/`

**Authentication:** Required

**Request Headers:**
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

**Success Response (204 No Content):**
```
No content returned
```

---

# 3. SUBSCRIPTIONS

## 3.1 List Subscription Plans

**Endpoint:** `GET /api/subscriptions/plans/`

**Authentication:** Not required

**Request Headers:**
```
Content-Type: application/json
```

**Success Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Free",
    "description": "Basic access to limited games",
    "price": "0.00",
    "duration_days": null,
    "features": {
      "max_downloads": 5,
      "ad_free": false,
      "exclusive_games": false
    },
    "is_active": true
  },
  {
    "id": 2,
    "name": "Premium Monthly",
    "description": "Full access to all games",
    "price": "9.99",
    "duration_days": 30,
    "features": {
      "max_downloads": null,
      "ad_free": true,
      "exclusive_games": true
    },
    "is_active": true
  },
  {
    "id": 3,
    "name": "Premium Yearly",
    "description": "Full access to all games (Best Value)",
    "price": "99.99",
    "duration_days": 365,
    "features": {
      "max_downloads": null,
      "ad_free": true,
      "exclusive_games": true
    },
    "is_active": true
  }
]
```

---

## 3.2 Get Plan Details

**Endpoint:** `GET /api/subscriptions/plans/{id}/`

**Authentication:** Not required

**Request Headers:**
```
Content-Type: application/json
```

**Success Response (200 OK):**
```json
{
  "id": 2,
  "name": "Premium Monthly",
  "description": "Full access to all games",
  "price": "9.99",
  "duration_days": 30,
  "features": {
    "max_downloads": null,
    "ad_free": true,
    "exclusive_games": true
  },
  "is_active": true
}
```

---

## 3.3 Create Subscription

**Endpoint:** `POST /api/subscriptions/subscriptions/`

**Authentication:** Required

**Request Headers:**
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
Content-Type: application/json
```

**Request Body:**
```json
{
  "plan": 2
}
```

**Required Fields:**
- `plan` (integer, plan ID)

**Success Response (201 Created):**
```json
{
  "id": 1,
  "user": 1,
  "plan": {
    "id": 2,
    "name": "Premium Monthly",
    "price": "9.99",
    "duration_days": 30
  },
  "status": "active",
  "start_date": "2025-11-16T10:30:00Z",
  "end_date": "2025-12-16T10:30:00Z",
  "auto_renew": true,
  "created_at": "2025-11-16T10:30:00Z"
}
```

**Note:** When subscription status becomes `active`, user's `is_premium` field is automatically set to `true` via Django signals.

**Subscription Status Values:**
- `active` - Currently active
- `cancelled` - User cancelled
- `expired` - Subscription ended

---

## 3.4 List My Subscriptions

**Endpoint:** `GET /api/subscriptions/subscriptions/`

**Authentication:** Required

**Request Headers:**
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

**Query Parameters:**
- `status` (string, optional): Filter by status (`active`, `cancelled`, `expired`)

**Success Response (200 OK):**
```json
[
  {
    "id": 1,
    "user": 1,
    "plan": {
      "id": 2,
      "name": "Premium Monthly",
      "price": "9.99",
      "duration_days": 30
    },
    "status": "active",
    "start_date": "2025-11-16T10:30:00Z",
    "end_date": "2025-12-16T10:30:00Z",
    "auto_renew": true,
    "created_at": "2025-11-16T10:30:00Z"
  }
]
```

---

## 3.5 Get Subscription Details

**Endpoint:** `GET /api/subscriptions/subscriptions/{id}/`

**Authentication:** Required

**Request Headers:**
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

**Success Response (200 OK):**
```json
{
  "id": 1,
  "user": 1,
  "plan": {
    "id": 2,
    "name": "Premium Monthly",
    "price": "9.99",
    "duration_days": 30
  },
  "status": "active",
  "start_date": "2025-11-16T10:30:00Z",
  "end_date": "2025-12-16T10:30:00Z",
  "auto_renew": true,
  "created_at": "2025-11-16T10:30:00Z"
}
```

---

## 3.6 Cancel Subscription

**Endpoint:** `PATCH /api/subscriptions/subscriptions/{id}/`

**Authentication:** Required

**Request Headers:**
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
Content-Type: application/json
```

**Request Body:**
```json
{
  "status": "cancelled",
  "auto_renew": false
}
```

**Success Response (200 OK):**
```json
{
  "id": 1,
  "user": 1,
  "plan": {
    "id": 2,
    "name": "Premium Monthly",
    "price": "9.99",
    "duration_days": 30
  },
  "status": "cancelled",
  "start_date": "2025-11-16T10:30:00Z",
  "end_date": "2025-12-16T10:30:00Z",
  "auto_renew": false,
  "created_at": "2025-11-16T10:30:00Z"
}
```

**Note:** When subscription is cancelled or deleted, user's `is_premium` field is automatically set to `false` via Django signals.

---

# 4. PAYMENTS

## 4.1 Create Payment Intent (Stripe)

**Endpoint:** `POST /api/payments/create-payment-intent/`

**Authentication:** Required

**Request Headers:**
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
Content-Type: application/json
```

**Request Body:**
```json
{
  "plan_id": 2,
  "payment_method": "card"
}
```

**Required Fields:**
- `plan_id` (integer)

**Optional Fields:**
- `payment_method` (string, default: "card")

**Success Response (200 OK):**
```json
{
  "client_secret": "pi_3OxxxxxxxxxxxxxxxxxxxXXX_secret_yyyyyyyyyyyyyyyYYYY",
  "payment_intent_id": "pi_3OxxxxxxxxxxxxxxxxxxxXXX",
  "amount": 999,
  "currency": "usd"
}
```

**Usage:**
Use the `client_secret` with Stripe SDK on the frontend to complete the payment.

---

## 4.2 List Payment History

**Endpoint:** `GET /api/payments/payments/`

**Authentication:** Required

**Request Headers:**
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

**Query Parameters:**
- `status` (string, optional): Filter by status (`pending`, `completed`, `failed`)
- `page` (integer, optional): Page number

**Success Response (200 OK):**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "user": 1,
      "subscription": {
        "id": 1,
        "plan": {
          "name": "Premium Monthly"
        }
      },
      "amount": "9.99",
      "currency": "USD",
      "status": "completed",
      "payment_method": "card",
      "stripe_payment_intent_id": "pi_3OxxxxxxxxxxxxxxxxxxxXXX",
      "created_at": "2025-11-16T10:30:00Z"
    }
  ]
}
```

---

## 4.3 Get Payment Details

**Endpoint:** `GET /api/payments/payments/{id}/`

**Authentication:** Required

**Request Headers:**
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

**Success Response (200 OK):**
```json
{
  "id": 1,
  "user": 1,
  "subscription": {
    "id": 1,
    "plan": {
      "id": 2,
      "name": "Premium Monthly",
      "price": "9.99"
    }
  },
  "amount": "9.99",
  "currency": "USD",
  "status": "completed",
  "payment_method": "card",
  "stripe_payment_intent_id": "pi_3OxxxxxxxxxxxxxxxxxxxXXX",
  "created_at": "2025-11-16T10:30:00Z"
}
```

---

## 4.4 Stripe Webhook

**Endpoint:** `POST /api/payments/webhook/stripe/`

**Authentication:** Not required (Stripe signature verification)

**Request Headers:**
```
Content-Type: application/json
Stripe-Signature: t=1492774577,v1=5257a869e7ecebeda32affa62cdca3fa51cad7e77a0e56ff536d0ce8e108d8bd
```

**Note:** This endpoint is called by Stripe servers. Configure in Stripe Dashboard:
```
Webhook URL: https://yourdomain.com/api/payments/webhook/stripe/
Events to send: payment_intent.succeeded, payment_intent.payment_failed
```

---

# Common Headers

## For All Authenticated Requests:
```
Authorization: Token <your-token-here>
Content-Type: application/json
```

## For File Uploads:
```
Authorization: Token <your-token-here>
Content-Type: multipart/form-data
```

## For Google OAuth:
```
Content-Type: application/json
```

---

# Error Responses

## Standard Error Format:

### 400 Bad Request
```json
{
  "field_name": ["Error message here"]
}
```

Or:
```json
{
  "error": "Error message here"
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

Or:
```json
{
  "detail": "Invalid token."
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

### 429 Too Many Requests
```json
{
  "error": "Too many requests. Please wait before trying again."
}
```

### 500 Internal Server Error
```json
{
  "error": "An unexpected error occurred. Please try again later."
}
```

---

# Rate Limiting

## OTP Requests:
- **Maximum:** 3 requests per 15 minutes per email
- **Endpoints affected:**
  - `/api/users/register/`
  - `/api/users/resend-otp/`
  - `/api/users/password-reset/request/`

---

# Pagination

Most list endpoints support pagination with these query parameters:

- `page` (integer): Page number (default: 1)
- `page_size` (integer): Items per page (default: 10, max: 100)

**Example:**
```
GET /api/games/games/?page=2&page_size=20
```

**Response includes:**
```json
{
  "count": 150,
  "next": "http://localhost:8000/api/games/games/?page=3&page_size=20",
  "previous": "http://localhost:8000/api/games/games/?page=1&page_size=20",
  "results": [...]
}
```

---

# Search & Filtering

## Games Filtering Examples:

```
# Search by title
GET /api/games/games/?search=god

# Filter by emulator
GET /api/games/games/?emulator=1

# Filter by minimum rating
GET /api/games/games/?rating_min=4.5

# Filter by tag
GET /api/games/games/?tags=1

# Combine filters
GET /api/games/games/?emulator=1&rating_min=4.0&search=war

# Order results
GET /api/games/games/?ordering=-rating  # Descending
GET /api/games/games/?ordering=title    # Ascending
```

## Subscriptions Filtering:

```
# Filter by status
GET /api/subscriptions/subscriptions/?status=active
```

## Payments Filtering:

```
# Filter by status
GET /api/payments/payments/?status=completed
```

---

# Testing with cURL

## Register User:
```bash
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
    "first_name": "Test",
    "last_name": "User"
  }'
```

## Login:
```bash
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```

## Get Games (Authenticated):
```bash
curl -X GET http://localhost:8000/api/games/games/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

## Download Game:
```bash
curl -X POST http://localhost:8000/api/games/games/1/download/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json"
```

## Change Password (Logged In):
```bash
curl -X POST http://localhost:8000/api/users/change-password/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "OldPassword123!",
    "new_password": "NewSecurePass456!",
    "confirm_password": "NewSecurePass456!"
  }'
```

## Forgot Password (Request OTP):
```bash
curl -X POST http://localhost:8000/api/users/password-reset/request/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com"
  }'
```

## Reset Password (With OTP):
```bash
curl -X POST http://localhost:8000/api/users/password-reset/reset/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "otp": "123456",
    "new_password": "NewSecurePass123!",
    "confirm_password": "NewSecurePass123!"
  }'
```

---

# Notes

1. **Premium Status Auto-Update:**
   - When a subscription becomes `active`, user's `is_premium` is set to `true`
   - When subscription is `cancelled` or deleted, `is_premium` becomes `false`
   - This happens automatically via Django signals

2. **Email Verification:**
   - OTP codes expire after 10 minutes
   - Users must verify email before logging in (unless signed up with Google)
   - Google users are automatically email-verified

3. **Google Sign-In:**
   - Users who sign up with Google cannot login with email/password
   - They must continue using Google Sign-In
   - Email/password users can only use email/password login

4. **Password Management:**
   - **Change Password** (`/change-password/`): For logged-in users who remember their password
     - Requires authentication token
     - Must provide old password for verification
     - No OTP needed
     - Issues new token after successful change
   
   - **Reset Password** (`/password-reset/reset/`): For users who forgot their password
     - No authentication required
     - Uses OTP sent to email
     - OTP expires in 10 minutes
     - Rate limited (3 requests per 15 minutes)

5. **File Uploads:**
   - Use `multipart/form-data` for profile pictures and game covers
   - Maximum file size: 10MB
   - Allowed formats: JPG, PNG, GIF

6. **Tokens:**
   - Tokens do not expire
   - Store securely on client side
   - Include in `Authorization` header for all authenticated requests
   - New token issued after password change (old token invalidated)

7. **Email Configuration:**
   - Sender: `agames.app.dev@gmail.com`
   - Daily limit: 500 emails (Gmail free account)
   - All OTP emails use purple gradient HTML templates

---

**End of Documentation**

For more information, visit the project repository or contact support.
