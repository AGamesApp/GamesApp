# AGames API Endpoints Reference
**Version:** 1.0  
**Base URL:** `https://games.agames.cv/api/`  
**Domain:** games.agames.cv  
**Date:** December 5, 2025

---

## Table of Contents
1. [Authentication](#authentication)
2. [Health Check](#health-check)
3. [Users & Auth](#users--auth)
4. [Games](#games)
5. [Emulators](#emulators)
6. [Subscriptions](#subscriptions)
7. [Notifications](#notifications)
8. [Support](#support)
9. [Pages](#pages)
10. [Search Techniques](#search-techniques)
11. [Caching](#caching)
12. [Email Configuration](#email-configuration)

---

## Authentication

### Headers for Authenticated Requests
```http
Authorization: Token <your_token_here>
Content-Type: application/json
```

### Rate Limits
- **Logged-in users:** 50 requests/minute
- **Anonymous users:** 20 requests/minute
- **Login endpoint:** 8 requests/minute
- **OTP resend:** 3 requests/minute
- **Password reset:** 3 requests/minute

---

## Health Check

### System Health Status
```http
GET /health/
```

**Success Response (200):**
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

**Unhealthy Response (503):**
```json
{
  "status": "unhealthy",
  "checks": {
    "database": "ok",
    "cache": "error: connection refused",
    "filesystem": "ok"
  }
}
```

**Use Cases:**
- **Uptime Monitoring:** UptimeRobot, Pingdom
- **Load Balancer Health Checks**
- **Quick System Status Verification**

**What it checks:**
- PostgreSQL database connection
- Redis cache availability
- File system write permissions

---

## Users & Auth

### 1. Register User (Email/Password)
```http
POST /api/users/register/
Content-Type: application/json
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePassword123!",
  "password_confirm": "SecurePassword123!"
}
```

**Success Response (201):**
```json
{
  "message": "Registration successful! Please check your email for the verification code.",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "profile_picture": null,
    "is_premium": false,
    "is_email_verified": false,
    "created_at": "2025-12-05T01:38:26.990257Z"
  },
  "token": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0"
}
```

**Error Response (400):**
```json
{
  "email": ["User with this email already exists."],
  "username": ["User with this username already exists."],
  "password": ["This password is too common."]
}
```
```json
{
  "non_field_errors": ["Passwords do not match"]
}
```

**Field Requirements:**
- **email:** Valid email format, must be unique
- **username:** 3-150 characters, must be unique, alphanumeric and @/./+/-/_ only
- **password:** Minimum 8 characters, must meet complexity requirements
- **password_confirm:** Must match password exactly

**Notes:**
- OTP is automatically sent to the provided email upon successful registration
- User account is created but not verified (is_email_verified = false)
- OTP is valid for 10 minutes

---

### 2. Login (Email/Password)
```http
POST /api/users/login/
Content-Type: application/json
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Success Response (200):**
```json
{
  "token": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "profile_picture": null,
    "is_premium": false,
    "is_email_verified": true,
    "created_at": "2025-12-05T01:38:26.990257Z"
  }
}
```

**Error Response (403 - Email Not Verified):**
```json
{
  "error": "Email verification required",
  "message": "Your email address is not verified. Please check your email inbox and verify your account before logging in.",
  "email": "user@example.com"
}
```

**Error Response (401 - Invalid Credentials):**
```json
{
  "error": "Invalid credentials"
}
```

---

### 3. Google OAuth Login
```http
POST /api/users/auth/google/
Content-Type: application/json
```

**Request Body:**
```json
{
  "id_token": "google_id_token_here"
}
```

**Success Response (200):**
```json
{
  "message": "Login successful",
  "token": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0",
  "user": {
    "id": 2,
    "email": "user@gmail.com",
    "username": "user",
    "profile_picture": "/media/profile_pictures/google_2_user.jpg",
    "is_premium": false,
    "is_email_verified": true,
    "created_at": "2025-12-05T01:38:26.990257Z"
  },
  "is_new_user": false
}
```

**Note:** Profile picture is automatically downloaded from Google and saved to user's profile.

**Error Response (400 - Invalid Token):**
```json
{
  "error": "Invalid Google token"
}
```

**Error Response (400 - Email Not Verified by Google):**
```json
{
  "error": "Google email is not verified"
}
```

---

### 4. Verify Email OTP
```http
POST /api/users/verify-otp/
Content-Type: application/json
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "otp": "123456"
}
```

**Success Response (200):**
```json
{
  "message": "Email verified successfully! You can now login.",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "profile_picture": null,
    "is_premium": false,
    "is_email_verified": true,
    "created_at": "2025-12-05T01:38:26.990257Z"
  }
}
```

**Error Response (400):**
```json
{
  "error": "Invalid or expired OTP. Please request a new one."
}
```

**Error Response (404):**
```json
{
  "error": "User with this email does not exist."
}
```

**Already Verified (200):**
```json
{
  "message": "Email is already verified. You can login now."
}
```

---

### 5. Resend OTP
```http
POST /api/users/resend-otp/
Content-Type: application/json
```

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Success Response (200):**
```json
{
  "message": "OTP has been resent to your email.",
  "email": "user@example.com"
}
```

**Error Response (404):**
```json
{
  "error": "User with this email does not exist."
}
```

**Already Verified (200):**
```json
{
  "message": "Email is already verified. You can login now."
}
```

**Notes:**
- Rate limited to 3 requests per minute
- OTP is valid for 10 minutes
- New OTP invalidates previous one

---

### 6. Request Password Reset
```http
POST /api/users/password-reset/request/
Content-Type: application/json
```

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Success Response (200):**
```json
{
  "message": "If an account with this email exists, a password reset code has been sent."
}
```

**Notes:**
- OTP is sent to the user's email
- OTP valid for 10 minutes
- For security, always returns success even if email doesn't exist
- Rate limited to 3 requests per minute

**Example OTP Email:**
- **Subject:** "Password Reset Code - AGames"
- **Body:** "Your password reset code is: 970521"

---

### 7. Verify Password Reset OTP
```http
POST /api/users/password-reset/verify-otp/
Content-Type: application/json
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "otp": "970521"
}
```

**Success Response (200):**
```json
{
  "message": "OTP verified successfully. You can now reset your password."
}
```

**Error Response (400):**
```json
{
  "error": "Invalid or expired OTP"
}
```

---

### 8. Reset Password
```http
POST /api/users/password-reset/reset/
Content-Type: application/json
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "otp": "970521",
  "new_password": "NewSecurePassword123!",
  "confirm_password": "NewSecurePassword123!"
}
```

**Success Response (200):**
```json
{
  "message": "Password reset successfully. You can now login with your new password."
}
```

**Error Responses (400):**
```json
{
  "error": "Invalid or expired OTP"
}
```
```json
{
  "error": "Passwords do not match"
}
```
```json
{
  "new_password": ["This password is too common."]
}
```

**Password Requirements:**
- Minimum 8 characters
- Must contain uppercase and lowercase letters
- Must contain at least one number
- Must contain at least one special character

---

### 9. Change Password (Authenticated)
```http
POST /api/users/change-password/
Authorization: Token <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "old_password": "OldPassword123!",
  "new_password": "NewPassword123!",
  "confirm_password": "NewPassword123!"
}
```

**Success Response (200):**
```json
{
  "message": "Password changed successfully"
}
```

**Error Response (400):**
```json
{
  "error": "Old password is incorrect"
}
```

---

### 10. Get User Profile
```http
GET /api/users/profile/
Authorization: Token <token>
```

**Success Response (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "profile_picture": "/media/profile_pictures/user_1.jpg",
  "is_premium": false,
  "is_email_verified": true,
  "created_at": "2025-12-01T10:00:00Z"
}
```

**Note:** 
- `profile_picture` will be `null` if no picture is uploaded
- `is_premium`, `is_email_verified`, and `created_at` are read-only fields

---

### 7. Update User Profile

**Option 1: Update Username Only (JSON)**
```http
PATCH /api/users/profile/
Authorization: Token <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "username": "john_updated"
}
```

**Option 2: Update Username and Profile Picture Together (Form Data)**
```http
PATCH /api/users/profile/
Authorization: Token <token>
Content-Type: multipart/form-data
```

**Request Body (Form Data):**
- `username`: "john_updated" (text field)
- `profile_picture`: image file (file field)

**JavaScript Example:**
```javascript
const formData = new FormData();
formData.append('username', 'john_updated');
formData.append('profile_picture', imageFile);

fetch('https://games.agames.cv/api/users/profile/', {
  method: 'PATCH',
  headers: {
    'Authorization': 'Token your-token-here'
    // Don't set Content-Type - browser sets it automatically
  },
  body: formData
});
```

**Success Response (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "john_updated",
  "profile_picture": "/media/profile_pictures/user_1_updated.jpg",
  "is_premium": false,
  "is_email_verified": true,
  "created_at": "2025-12-01T10:00:00Z"
}
```

**Notes:**
- You can update `username` and `profile_picture` in the same request using form data
- For username only, use JSON (simpler)
- For profile picture with or without username, use form data
- Fields `id`, `email`, `is_premium`, `is_email_verified`, `created_at` are read-only

---
  "created_at": "2025-12-01T10:00:00Z"
}
```

---

### 8. Update Profile Picture (Simplified)
```http
POST /api/users/profile/picture/
Authorization: Token <token>
Content-Type: multipart/form-data
```

**Request Body (Form Data):**
- `profile_picture`: Image file (JPG, PNG, GIF, WEBP)

**Success Response (200):**
```json
{
  "message": "Profile picture updated successfully",
  "profile_picture": "https://games.agames.cv/media/profile_pictures/user_1_profile.jpg"
}
```

**Error Responses:**

**400 - No File:**
```json
{
  "error": "No profile picture provided",
  "message": "Please upload an image file with key \"profile_picture\""
}
```

**400 - Invalid File Type:**
```json
{
  "error": "Invalid file type",
  "message": "Only image files (JPG, PNG, GIF, WEBP) are allowed"
}
```

**400 - File Too Large:**
```json
{
  "error": "File too large",
  "message": "Profile picture must be less than 5MB"
}
```

**Mobile/JavaScript Example:**
```javascript
const formData = new FormData();
formData.append('profile_picture', imageFile);

fetch('https://games.agames.cv/api/users/profile/picture/', {
  method: 'POST',
  headers: {
    'Authorization': 'Token your-token-here'
    // Don't set Content-Type - let browser handle it
  },
  body: formData
});
```

**cURL Example:**
```bash
curl -X POST https://games.agames.cv/api/users/profile/picture/ \
  -H "Authorization: Token your-token-here" \
  -F "profile_picture=@/path/to/image.jpg"
```

---

### 8. Logout
```http
POST /api/users/logout/
Authorization: Token <token>
```

**Success Response (200):**
```json
{
  "message": "Successfully logged out"
}
```

---

## Games

### 1. List All Games (Paginated)
```http
GET /api/games/
```

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `page_size` (int): Items per page (default: 20, max: 50)
- `emulator` (int): Filter by emulator ID
- `is_premium` (bool): Filter premium games (true/false)
- `genres` (int): Filter by genre ID
- `ordering` (string): Sort by field (title, created_at, year, views, downloads)
- `search` (string): Search in title

**Example:**
```http
GET /api/games/?emulator=1&page=1&page_size=20&ordering=-views
```

**Success Response (200):**
```json
{
  "count": 150,
  "next": "https://games.agames.cv/api/games/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Super Mario 64",
      "image_url": "https://example.com/mario64.jpg",
      "emulator": {
        "id": 1,
        "name": "Nintendo 64"
      },
      "size": "8MB",
      "year": "1996",
      "region": "USA",
      "is_premium": false,
      "rating": 4.8,
      "total_loves": 1250,
      "views": 15000,
      "downloads": 8500,
      "genres": [
        {"id": 1, "name": "Platform"},
        {"id": 2, "name": "Adventure"}
      ]
    }
  ]
}
```

---

### 2. Search Games (Advanced)
```http
GET /api/games/search/?q=<search_term>
```

**Advanced Search Features:**
- **Subsequence Matching:** Matches partial sequences (e.g., "sfii" matches "Street Fighter II")
- **Case-Insensitive:** Searches are not case-sensitive
- **Relevance Ranking:** Results sorted by relevance

**Query Parameters:**
- `q` (string): Search query (required)
- `emulator` (int): Filter by emulator
- `page` (int): Page number
- `page_size` (int): Items per page

**Example:**
```http
GET /api/games/search/?q=mario&emulator=1&page=1
```

**Success Response (200):**
```json
{
  "count": 25,
  "next": "https://games.agames.cv/api/games/search/?q=mario&page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Super Mario 64",
      "image_url": "https://example.com/mario64.jpg",
      "emulator": {"id": 1, "name": "Nintendo 64"},
      "relevance_score": 100,
      "rating": 4.8,
      "total_loves": 1250
    }
  ]
}
```

---

### 3. Get Game Details
```http
GET /api/games/{id}/
```

**Success Response (200):**
```json
{
  "id": 1,
  "title": "Super Mario 64",
  "emulator": {
    "id": 1,
    "name": "Nintendo 64",
    "icon": "https://example.com/n64.png"
  },
  "image_url": "https://example.com/mario64.jpg",
  "size": "8MB",
  "download_url": "https://example.com/mario64.z64",
  "game_url": "https://example.com/mario64-info",
  "video_url": "https://youtube.com/watch?v=xxx",
  "region": "USA",
  "year": "1996",
  "is_premium": false,
  "genres": [
    {"id": 1, "name": "Platform"},
    {"id": 2, "name": "Adventure"}
  ],
  "rating": 4.8,
  "total_loves": 1250,
  "views": 15000,
  "downloads": 8500,
  "user_rating": 5,
  "user_loved": true,
  "images": [
    {
      "id": 1,
      "image_url": "https://example.com/screenshot1.jpg",
      "caption": "Gameplay Screenshot"
    }
  ],
  "additional_files": [
    {
      "id": 1,
      "file_name": "Texture Pack",
      "download_link": "https://example.com/textures.zip"
    }
  ]
}
```

---

### 4. Increment Game Views
```http
POST /api/games/{id}/increment_views/
```

**Success Response (200):**
```json
{
  "views": 15001,
  "message": "Views incremented successfully"
}
```

---

### 5. Increment Game Downloads
```http
POST /api/games/{id}/increment_downloads/
```

**Success Response (200):**
```json
{
  "downloads": 8501,
  "message": "Downloads incremented successfully"
}
```

---

### 6. Rate Game
```http
POST /api/games/{id}/rate/
Authorization: Token <token>
Content-Type: application/json
```

**Description:**
- Submit or update a rating for a game (separate from reviews)
- Each user can only have one rating per game
- Score must be between 1-5 in 0.5 increments

**Request Body:**
```json
{
  "score": 4.5
}
```

**Success Response - Created (201):**
```json
{
  "message": "Rating created successfully",
  "rating": {
    "id": 1,
    "user": 2,
    "user_email": "user@example.com",
    "game": 1,
    "game_title": "Super Mario 64",
    "score": 4.5,
    "created_at": "2025-12-07T10:30:00Z",
    "updated_at": "2025-12-07T10:30:00Z"
  }
}
```

**Success Response - Updated (200):**
```json
{
  "message": "Rating updated successfully",
  "rating": {
    "id": 1,
    "user": 2,
    "user_email": "user@example.com",
    "game": 1,
    "game_title": "Super Mario 64",
    "score": 5.0,
    "created_at": "2025-12-07T10:30:00Z",
    "updated_at": "2025-12-07T15:45:00Z"
  }
}
```

**Error Response - Missing Score (400):**
```json
{
  "error": "Score is required"
}
```

**Error Response - Invalid Range (400):**
```json
{
  "error": "Score must be between 1 and 5"
}
```

**Error Response - Invalid Increment (400):**
```json
{
  "error": "Score must be in 0.5 increments (e.g., 1.0, 1.5, 2.0)"
}
```

---

### 7. Get Game Ratings
```http
GET /api/games/{id}/ratings/
```

**Description:**
- Returns paginated list of all ratings for a game
- Does not require authentication
- Shows user email, score, and timestamps

**Success Response (200):**
```json
{
  "count": 45,
  "next": "https://games.agames.cv/api/games/1/ratings/?page=2",
  "previous": null,
  "results": [
    {
      "id": 10,
      "user": 5,
      "user_email": "user@example.com",
      "game": 1,
      "game_title": "Super Mario 64",
      "score": "4.5",
      "created_at": "2025-12-07T10:30:00Z",
      "updated_at": "2025-12-07T10:30:00Z"
    },
    {
      "id": 9,
      "user": 3,
      "user_email": "another@example.com",
      "game": 1,
      "game_title": "Super Mario 64",
      "score": "5.0",
      "created_at": "2025-12-06T14:20:00Z",
      "updated_at": "2025-12-06T14:20:00Z"
    }
  ]
}
```

---

### 8. Love/Unlike Game
```http
POST /api/games/{id}/love/
Authorization: Token <token>
```

**Success Response (200):**
```json
{
  "loved": true,
  "total_loves": 1251,
  "message": "Game added to favorites"
}
```

**Unlike Response (200):**
```json
{
  "loved": false,
  "total_loves": 1250,
  "message": "Game removed from favorites"
}
```

---

### 9. Submit or Update Game Review and Rating
```http
POST /api/games/{id}/review/
PUT /api/games/{id}/review/
Authorization: Token <token>
Content-Type: application/json
```

**Description:**
- Each user can only have **one review** per game
- If user already has a review, it will be **updated** (not duplicated)
- Both `review` and `score` are **optional**, but **at least one must be provided**
- Score must be between 1-5 in 0.5 increments if provided

**Request Body (Both Fields):**
```json
{
  "review": "Amazing game! Brings back childhood memories.",
  "score": 4.5
}
```

**Request Body (Review Only):**
```json
{
  "review": "Great gameplay and graphics!"
}
```

**Request Body (Score Only):**
```json
{
  "score": 4.5
}
```

**Success Response - Created (201):**
```json
{
  "message": "Review created successfully",
  "data": {
    "review": "Amazing game! Brings back childhood memories.",
    "score": 4.5,
    "profile_picture": "https://games.agames.cv/media/profile_pictures/user123.jpg",
    "username": "johndoe",
    "comment_date": "2025-12-07T10:30:00Z"
  }
}
```

**Success Response - Updated (200):**
```json
{
  "message": "Review updated successfully",
  "data": {
    "review": "Amazing game! Updated my review after playing more.",
    "score": 5.0,
    "profile_picture": "https://games.agames.cv/media/profile_pictures/user123.jpg",
    "username": "johndoe",
    "comment_date": "2025-12-07T15:45:00Z"
  }
}
```

**Success Response - Score Only (201):**
```json
{
  "message": "Review created successfully",
  "data": {
    "review": "",
    "score": 4.5,
    "profile_picture": "https://games.agames.cv/media/profile_pictures/user123.jpg",
    "username": "johndoe",
    "comment_date": "2025-12-07T10:30:00Z"
  }
}
```

**Error Response - No Fields Provided (400):**
```json
{
  "error": "At least review text or score must be provided"
}
```

**Error Response - Invalid Score (400):**
```json
{
  "error": "Score must be between 1 and 5"
}
```

**Error Response - Invalid Score Increment (400):**
```json
{
  "error": "Score must be in 0.5 increments (e.g., 1.0, 1.5, 2.0)"
}
```

---

### 10. Get Game Reviews
```http
GET /api/games/{id}/reviews/
```

**Description:**
- Returns paginated list of all reviews for a game
- Includes user information, review text, score, and timestamp
- Reviews are ordered by most recent first

**Success Response (200):**
```json
{
  "count": 45,
  "next": "https://games.agames.cv/api/games/1/reviews/?page=2",
  "previous": null,
  "results": [
    {
      "id": 10,
      "review": "Amazing game! Brings back childhood memories.",
      "score": 4.5,
      "profile_picture": "https://games.agames.cv/media/profile_pictures/user123.jpg",
      "username": "johndoe",
      "comment_date": "2025-12-07T10:30:00Z"
    },
    {
      "id": 9,
      "review": "Great gameplay but difficult controls.",
      "score": 3.5,
      "profile_picture": null,
      "username": "janedoe",
      "comment_date": "2025-12-06T14:20:00Z"
    }
  ]
}
```

---

### 11. Get My Review for a Game
```http
GET /api/games/{id}/my_review/
Authorization: Token <token>
```

**Description:**
- Returns the authenticated user's review for a specific game
- Useful to check if user already reviewed a game and pre-fill edit forms

**Success Response (200):**
```json
{
  "id": 10,
  "review": "Amazing game! Brings back childhood memories.",
  "score": 4.5,
  "profile_picture": "https://games.agames.cv/media/profile_pictures/user123.jpg",
  "username": "johndoe",
  "comment_date": "2025-12-07T10:30:00Z"
}
```

**Error Response - Not Found (404):**
```json
{
  "error": "You have not reviewed this game yet"
}
```

---

### 12. Get My Reviews (All Games)
```http
GET /api/games/my_reviews/
Authorization: Token <token>
```

**Description:**
- Returns all reviews by the authenticated user across all games
- Includes game information for each review

**Success Response (200):**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 10,
      "game_id": 1,
      "game_title": "Super Mario 64",
      "review": "Amazing game! Brings back childhood memories.",
      "score": 4.5,
      "profile_picture": "https://games.agames.cv/media/profile_pictures/user123.jpg",
      "username": "johndoe",
      "comment_date": "2025-12-07T10:30:00Z"
    },
    {
      "id": 8,
      "game_id": 5,
      "game_title": "The Legend of Zelda",
      "review": "Classic adventure game.",
      "score": 5.0,
      "profile_picture": "https://games.agames.cv/media/profile_pictures/user123.jpg",
      "username": "johndoe",
      "comment_date": "2025-12-05T09:15:00Z"
    }
  ]
}
```

---

### 13. Get User's Loved Games
```http
GET /api/games/my_loved_games/
Authorization: Token <token>
```

**Query Parameters:**
- `emulator` (optional) - Filter by emulator ID (e.g., `?emulator=1`)

**Examples:**
```bash
# Get all loved games
GET /api/games/my_loved_games/

# Get loved games for specific emulator
GET /api/games/my_loved_games/?emulator=1
```

**Success Response (200):**
```json
{
  "count": 15,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Super Mario 64",
      "description": "Classic 3D platformer...",
      "image_url": "https://example.com/mario64.jpg",
      "views": 5000,
      "average_rating": 4.8,
      "total_loves": 350,
      "total_downloads": 1200
    }
  ]
}
```

---

### 14. Get App Details
```http
GET /api/app_details/
```

**Description:** Get application configuration and status. No authentication required.

**Success Response (200):**
```json
{
  "app_version": "1.0.0",
  "app_link": "https://play.google.com/store/apps/details?id=get.orepsp2.emulatorgame",
  "under_maintenance": false
}
```

**Usage:**
- Check `under_maintenance` to show maintenance screen to users
- Use `app_link` to redirect users to update the app
- Display `app_version` for version checking

---

## Emulators

### 1. List All Emulators
```http
GET /api/emulators/
```

**Query Parameters:**
- `search` (string): Search emulator names
- `ordering` (string): Sort by field (name, created_at)

**Success Response (200):**
```json
{
  "count": 15,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Nintendo 64",
      "icon": "https://example.com/n64.png",
      "download_url": "https://example.com/n64emu.zip",
      "video_url": "https://youtube.com/watch?v=tutorial",
      "open_outside": false,
      "additional_files": [
        {
          "id": 1,
          "file_name": "BIOS Files",
          "download_link": "https://example.com/bios.zip",
          "description": "Required BIOS files"
        }
      ],
      "created_at": "2025-11-01T10:00:00Z"
    }
  ]
}
```

**Cache:** 10 minutes

---

### 2. Get Emulator Details
```http
GET /api/emulators/{id}/
```

**Success Response (200):**
```json
{
  "id": 1,
  "name": "Nintendo 64",
  "icon": "https://example.com/n64.png",
  "download_url": "https://example.com/n64emu.zip",
  "video_url": "https://youtube.com/watch?v=tutorial",
  "open_outside": false,
  "additional_files": [
    {
      "id": 1,
      "file_name": "BIOS Files",
      "download_link": "https://example.com/bios.zip",
      "description": "Required BIOS files"
    }
  ],
  "created_at": "2025-11-01T10:00:00Z",
  "total_games": 150
}
```

**Cache:** 10 minutes

---

## Subscriptions

### 1. Get Subscription Plans
```http
GET /api/subscriptions/plans/
```

**Success Response (200):**
```json
{
  "count": 3,
  "results": [
    {
      "id": 1,
      "name": "Monthly Premium",
      "price": "9.99",
      "duration_days": 30,
      "features": [
        "Unlimited game downloads",
        "Ad-free experience",
        "Early access to new games",
        "Priority support"
      ],
      "is_active": true
    }
  ]
}
```

---

### 2. Subscribe to Plan
```http
POST /api/subscriptions/subscribe/
Authorization: Token <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "plan_id": 1,
  "payment_method": "stripe",
  "stripe_token": "tok_visa"
}
```

**Success Response (201):**
```json
{
  "id": 5,
  "user": 1,
  "plan": {
    "id": 1,
    "name": "Monthly Premium",
    "price": "9.99"
  },
  "start_date": "2025-12-05",
  "end_date": "2026-01-04",
  "is_active": true,
  "payment_status": "completed"
}
```

---

### 3. Get User Subscription
```http
GET /api/subscriptions/my-subscription/
Authorization: Token <token>
```

**Success Response (200):**
```json
{
  "id": 5,
  "plan": {
    "id": 1,
    "name": "Monthly Premium",
    "price": "9.99"
  },
  "start_date": "2025-12-05",
  "end_date": "2026-01-04",
  "is_active": true,
  "days_remaining": 30
}
```

---

### 4. Cancel Subscription
```http
POST /api/subscriptions/{id}/cancel/
Authorization: Token <token>
```

**Success Response (200):**
```json
{
  "message": "Subscription cancelled successfully",
  "end_date": "2026-01-04",
  "note": "You can still access premium features until the end date"
}
```

---

## Notifications

### 1. Get User Notifications
```http
GET /api/notifications/
Authorization: Token <token>
```

**Query Parameters:**
- `is_read` (bool): Filter by read status
- `page` (int): Page number

**Success Response (200):**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 15,
      "title": "New Game Added!",
      "body": "Check out the new Super Mario 64 game",
      "notification_type": "new_game",
      "is_read": false,
      "created_at": "2025-12-05T10:00:00Z",
      "data": {
        "game_id": 1
      }
    }
  ]
}
```

---

### 2. Mark Notification as Read
```http
POST /api/notifications/{id}/mark_read/
Authorization: Token <token>
```

**Success Response (200):**
```json
{
  "message": "Notification marked as read"
}
```

---

### 3. Delete All Notifications
```http
POST /api/notifications/mark_all_read/
Authorization: Token <token>
```

**Description:** Deletes all notifications for the authenticated users.


**Success Response (200):**
```json
{
  "message": "10 notifications deleted",
  "count": 10
}
```

---

### 4. Register FCM Token (Push Notifications)
```http
POST /api/notifications/register-token/
Authorization: Token <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "fcm_token": "firebase_cloud_messaging_token_here",
  "device_type": "android"
}
```

**Success Response (200):**
```json
{
  "message": "FCM token registered successfully"
}
```

---

## Support

### 1. Send Support Message

**Anonymous Users (No Authentication Required):**
```http
POST /api/support/messages/
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "subject": "Game download issue",
  "message": "I can't download Need For Speed. It shows error 404."
}
```

**Required Fields:**
- `name` (string, max 200 chars) - Required for anonymous users
- `email` (email) - Required for anonymous users
- `subject` (string, max 300 chars) - **Required** for all users
- `message` (text) - **Required** for all users

**Success Response (201):**
```json
{
  "id": 8,
  "user": null,
  "user_email": null,
  "name": "John Doe",
  "email": "john@example.com",
  "subject": "Game download issue",
  "message": "I can't download Need For Speed. It shows error 404.",
  "status": "pending",
  "is_reviewed": false,
  "reviewed_at": null,
  "reviewed_by": null,
  "reviewed_by_username": null,
  "created_at": "2025-12-09T20:00:00Z",
  "updated_at": "2025-12-09T20:00:00Z"
}
```

---

**Authenticated Users:**
```http
POST /api/support/messages/
Authorization: Token <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "subject": "Game download issue",
  "message": "I can't download Need For Speed. It shows error 404."
}
```

**Note:** For authenticated users, `name` and `email` are auto-filled from user profile.

**Required Fields:**
- `subject` (string, max 300 chars) - **Required**
- `message` (text) - **Required**

**Success Response (201):**
```json
{
  "id": 9,
  "user": 12,
  "user_email": "ramy41599@gmail.com",
  "name": "RamyRashad",
  "email": "ramy41599@gmail.com",
  "subject": "Game download issue",
  "message": "I can't download Need For Speed. It shows error 404.",
  "status": "pending",
  "is_reviewed": false,
  "reviewed_at": null,
  "reviewed_by": null,
  "reviewed_by_username": null,
  "created_at": "2025-12-09T20:00:00Z",
  "updated_at": "2025-12-09T20:00:00Z"
}
```

**Error Responses:**

**400 Bad Request** - Missing required fields:
```json
{
  "subject": ["This field is required."],
  "message": ["This field is required."]
}
```

**400 Bad Request** - Anonymous user missing name/email:
```json
{
  "name": ["This field is required for anonymous submissions."],
  "email": ["This field is required for anonymous submissions."]
}
```

---

### 2. Get User Messages (Admin Only)
```http
GET /api/support/messages/
Authorization: Token <admin_token>
```

**Query Parameters:**
- `is_reviewed` (boolean): Filter by review status (true/false)
- `status` (string): Filter by status (pending, reviewed)

**Success Response (200):**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 8,
      "user": null,
      "user_email": null,
      "name": "John Doe",
      "email": "john@example.com",
      "subject": "Game download issue",
      "message": "I can't download Need For Speed.",
      "status": "pending",
      "is_reviewed": false,
      "reviewed_at": null,
      "reviewed_by": null,
      "reviewed_by_username": null,
      "created_at": "2025-12-09T20:00:00Z",
      "updated_at": "2025-12-09T20:00:00Z"
    },
    {
      "id": 9,
      "user": 12,
      "user_email": "ramy41599@gmail.com",
      "name": "RamyRashad",
      "email": "ramy41599@gmail.com",
      "subject": "Feature request",
      "message": "Please add more games.",
      "status": "reviewed",
      "is_reviewed": true,
      "reviewed_at": "2025-12-09T19:00:00Z",
      "reviewed_by": 1,
      "reviewed_by_username": "agames",
      "created_at": "2025-12-09T18:00:00Z",
      "updated_at": "2025-12-09T19:00:00Z"
    }
  ]
}
```

---

### 3. Mark Message as Reviewed (Admin Only)
```http
POST /api/support/messages/{id}/mark_reviewed/
Authorization: Token <admin_token>
```

**Success Response (200):**
```json
{
  "status": "success",
  "message": "Message marked as reviewed by agames"
}
```

**Error Responses:**

**401 Unauthorized** - Not logged in:
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**403 Forbidden** - Not admin:
```json
{
  "detail": "You do not have permission to perform this action."
}
```

---

### 4. Mark Message as Pending (Admin Only)
```http
POST /api/support/messages/{id}/mark_pending/
Authorization: Token <admin_token>
```

**Success Response (200):**
```json
{
  "status": "success",
  "message": "Message marked as pending"
}
```

---

### Support Message Statuses

- **pending** - New message, not yet reviewed by admin
- **reviewed** - Message has been reviewed by admin

### Support Message Flow

1. User (anonymous or authenticated) sends support message via `POST /api/support/messages/`
2. Message is created with status `pending`
3. Admin views messages in dashboard at `/customadmin/support/`
4. Admin marks message as reviewed (status changes to `reviewed`)
5. Admin can mark it back to pending if needed

### Dashboard Access (Admin Only)

URL: `https://games.agames.cv/customadmin/support/`

Features:
- View all support messages
- Filter by status (All, Pending, Reviewed)
- Mark messages as reviewed with one click
- See who reviewed each message and when

---

**Success Response (201):**
```json
{
  "id": 30,
  "ticket": 25,
  "user": {
    "id": 1,
    "full_name": "John Doe"
  },
  "message": "Thank you! The issue is now resolved.",
  "created_at": "2025-12-05T13:00:00Z"
}
```

---

## Pages

### 1. Get Static Pages
```http
GET /api/pages/
```

**Success Response (200):**
```json
{
  "count": 3,
  "results": [
    {
      "id": 1,
      "title": "About Us",
      "slug": "about-us",
      "content": "<p>Welcome to AGames...</p>",
      "is_published": true,
      "created_at": "2025-11-01T10:00:00Z"
    }
  ]
}
```

---

### 2. Get Page by Slug
```http
GET /api/pages/{slug}/
```

**Example:**
```http
GET /api/pages/privacy-policy/
```

**Success Response (200):**
```json
{
  "id": 2,
  "title": "Privacy Policy",
  "slug": "privacy-policy",
  "content": "<h1>Privacy Policy</h1><p>Your privacy is important...</p>",
  "is_published": true,
  "created_at": "2025-11-01T10:00:00Z",
  "updated_at": "2025-12-01T10:00:00Z"
}
```

---

## Search Techniques

### 1. Basic Search
Simple text matching in game titles:
```http
GET /api/games/?search=mario
```

### 2. Advanced Subsequence Search
Matches partial character sequences with relevance ranking:
```http
GET /api/games/search/?q=sfii
```
- Matches: "**S**treet **F**ighter **II**"
- Matches: "**S**uper **F**inal Fantasy **II**"
- Ranked by relevance

### 3. Multi-Filter Search
Combine search with filters:
```http
GET /api/games/search/?q=mario&emulator=1&is_premium=false&genres=1
```

### 4. Search with Ordering
```http
GET /api/games/search/?q=zelda&ordering=-rating
```
**Ordering Options:**
- `title` / `-title` (A-Z / Z-A)
- `created_at` / `-created_at` (Oldest / Newest)
- `year` / `-year`
- `views` / `-views` (Least / Most viewed)
- `downloads` / `-downloads`
- `rating` / `-rating`

### 5. Fuzzy Matching Examples
The search handles:
- **Case insensitivity:** "MARIO" = "mario" = "MaRiO"
- **Subsequence matching:** "smb" matches "Super Mario Bros"
- **Partial words:** "zeld" matches "Zelda"

---

## Caching

### Cache Strategy
**Redis cache enabled with the following durations:**

| Endpoint Type | Cache Duration |
|--------------|----------------|
| Emulators List | 10 minutes |
| Emulator Detail | 10 minutes |
| Games List | 5 minutes |
| Game Detail | 10 minutes |
| Static Pages | 5 minutes |

### Cache Headers
Cached responses include:
```http
Cache-Control: max-age=300
ETag: "a1b2c3d4"
```

### Cache Invalidation
- **Automatic:** Expires after timeout
- **Manual:** Admin actions automatically clear related cache
- **Clear all:** Redis FLUSHDB (admin only)

### Performance
- **Cache Hit:** ~2-3ms response time
- **Cache Miss:** ~280-300ms response time
- **Hit Rate:** Typically 70-80%

---

## Error Responses

### 400 Bad Request
```json
{
  "field_name": ["Error message"],
  "non_field_errors": ["General error message"]
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
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
  "detail": "Request was throttled. Expected available in 45 seconds."
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error. Please try again later."
}
```

---

## Response Pagination

All paginated endpoints use this structure:
```json
{
  "count": 150,
  "next": "https://games.agames.cv/api/games/?page=3",
  "previous": "https://games.agames.cv/api/games/?page=1",
  "results": [...]
}
```

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `page_size` (int): Items per page (default: 20, max: 50)

---

## API Documentation UI

### Swagger UI
```
https://games.agames.cv/api/docs/
```
Interactive API documentation with "Try it out" functionality.

### ReDoc
```
https://games.agames.cv/api/redoc/
```
Clean, searchable API documentation.

### OpenAPI Schema
```
https://games.agames.cv/api/schema/
```
Download OpenAPI 3.0 schema in JSON format.

---

## Best Practices

### 1. Always Use HTTPS (When Available)
```http
# Use this in production
https://152.53.206.21/api/games/

# Current (HTTP only)
https://games.agames.cv/api/games/
```

### 2. Include Token in Headers
```http
Authorization: Token a1b2c3d4e5f6g7h8i9j0
```

### 3. Handle Rate Limits
Check response headers:
```http
X-RateLimit-Limit: 50
X-RateLimit-Remaining: 48
X-RateLimit-Reset: 1733400000
```

### 4. Use Pagination for Large Datasets
```http
GET /api/games/?page_size=50&page=1
```

### 5. Cache Responses on Client Side
Respect Cache-Control headers for better performance.

### 6. Error Handling
Always check HTTP status codes and handle errors appropriately.

---

## Email Configuration

### SMTP Settings
The API uses Gmail SMTP for sending emails (OTP verification, password reset, notifications).

**Current Configuration:**
- **SMTP Server:** smtp.gmail.com
- **Port:** 587 (TLS)
- **Sender Email:** agames.app.dev@gmail.com
- **From Name:** AGames

### Email Types Sent

#### 1. Email Verification OTP
**Trigger:** User registration or OTP request  
**Subject:** "Email Verification Code - AGames"  
**Contains:** 6-digit OTP code  
**Valid For:** 10 minutes

**Example:**
```
Subject: Email Verification Code - AGames

Hello,

Your email verification code is: 123456

This code will expire in 10 minutes.

Best regards,
AGames Team
```

#### 2. Password Reset OTP
**Trigger:** Password reset request  
**Subject:** "Password Reset Code - AGames"  
**Contains:** 6-digit OTP code  
**Valid For:** 10 minutes

**Example:**
```
Subject: Password Reset Code - AGames

Hello,

Your password reset code is: 970521

This code will expire in 10 minutes.

If you didn't request this, please ignore this email.

Best regards,
AGames Team
```

#### 3. Support Ticket Notifications
**Trigger:** New support ticket or reply  
**Subject:** "Support Ticket Update - AGames"  
**Contains:** Ticket details and reply content

### Email Rate Limits
- **OTP Requests:** 3 per minute per email
- **Password Reset:** 3 per minute per email
- **Support Notifications:** No limit

### Customizing Email Sender
To change the sender email, update in `/root/game/gamezone/settings.py`:

```python
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'  # Gmail App Password
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'
```

Or add to `.env` file:
```bash
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

**Note:** For Gmail, you need to:
1. Enable 2-Factor Authentication
2. Generate an App Password (not your regular password)
3. Use the App Password in the configuration

---

## Firebase Cloud Messaging (FCM)

### Configuration
**Service Account:** firebase-adminsdk-fbsvc@agames-21123.iam.gserviceaccount.com  
**Project ID:** agames-21123  
**Client ID:** 114457783983123047230

### Credentials Location
`/root/game/serviceAccountKey.json`

### Notification Types
- New game releases
- Subscription updates
- Support ticket replies
- System announcements

### Testing FCM
Send a test notification using the admin dashboard or API:
```http
POST /api/notifications/send/
Authorization: Token <admin_token>
Content-Type: application/json

{
  "user_id": 1,
  "title": "Test Notification",
  "message": "This is a test push notification",
  "type": "info"
}
```

---

## Changelog

### Version 1.0 (December 5, 2025)
- Initial API release
- Redis caching implemented (73% hit rate)
- Advanced search with subsequence matching
- FCM push notifications
- Support ticket system
- OAuth Google authentication
- Password reset with OTP
- Email verification system
- Health check endpoint
- 7 Gunicorn workers (1,000+ concurrent capacity)
- Gzip compression (40-60% reduction)
- 4GB swap space for stability

---

**Last Updated:** December 5, 2025  
**Maintained By:** AGames Development Team  
**Support:** support@agames.example.com
