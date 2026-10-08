# 🔐 AGames Google OAuth API - Mobile Client Guide

## Overview

AGames uses **API-based authentication** with tokens. Your mobile app should use Google Sign-In SDK and send the ID token to the backend.

---

## 📱 Client Implementation (Mobile App)

### Step 1: Configure Google Sign-In in Your App

**Android (build.gradle):**
```gradle
dependencies {
    implementation 'com.google.android.gms:play-services-auth:20.7.0'
}
```

**iOS (Podfile):**
```ruby
pod 'GoogleSignIn'
```

**Flutter (pubspec.yaml):**
```yaml
dependencies:
  google_sign_in: ^6.1.5
```

### Step 2: Get Google ID Token from Client SDK

**Flutter Example:**
```dart
import 'package:google_sign_in/google_sign_in.dart';

final GoogleSignIn _googleSignIn = GoogleSignIn(
  scopes: ['email', 'profile'],
  clientId: 'your-client-id.apps.googleusercontent.com',
);

Future<String?> signInWithGoogle() async {
  try {
    final GoogleSignInAccount? account = await _googleSignIn.signIn();
    if (account == null) return null;
    
    final GoogleSignInAuthentication auth = await account.authentication;
    return auth.idToken;  // ← This is what you send to backend
  } catch (error) {
    print('Error signing in: $error');
    return null;
  }
}
```

**Android (Kotlin):**
```kotlin
val gso = GoogleSignInOptions.Builder(GoogleSignInOptions.DEFAULT_SIGN_IN)
    .requestIdToken("your-client-id.apps.googleusercontent.com")
    .requestEmail()
    .build()

val googleSignInClient = GoogleSignIn.getClient(this, gso)

// After user signs in:
val account = GoogleSignIn.getLastSignedInAccount(this)
val idToken = account?.idToken  // ← Send this to backend
```

---

## 🚀 API Endpoint

### POST `/api/users/auth/google/`

**Base URL:** `https://games.agames.cv/api/users/auth/google/`

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjdlM..."
}
```

**Success Response (200 OK):**
```json
{
  "message": "Login successful",
  "user": {
    "id": 123,
    "email": "user@example.com",
    "username": "user",
    "is_email_verified": true,
    "is_premium": false,
    "premium_expires": null
  },
  "token": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
  "is_new_user": false
}
```

**Success Response (New User - 200 OK):**
```json
{
  "message": "Account created successfully",
  "user": {
    "id": 124,
    "email": "newuser@gmail.com",
    "username": "newuser",
    "is_email_verified": true,
    "is_premium": false,
    "premium_expires": null
  },
  "token": "x9y8z7w6v5u4t3s2r1q0p9o8n7m6l5k4",
  "is_new_user": true
}
```

**Error Responses:**

**400 Bad Request - Missing Token:**
```json
{
  "error": "id_token is required"
}
```

**400 Bad Request - Invalid Token:**
```json
{
  "error": "Invalid Google token"
}
```

**400 Bad Request - Email Not Verified:**
```json
{
  "error": "Google email is not verified"
}
```

---

## 💻 Complete Client Example (Flutter/Dart)

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:google_sign_in/google_sign_in.dart';

class AuthService {
  static const String baseUrl = 'https://games.agames.cv/api/users';
  
  final GoogleSignIn _googleSignIn = GoogleSignIn(
    scopes: ['email', 'profile'],
    clientId: 'your-client-id.apps.googleusercontent.com',
  );
  
  Future<Map<String, dynamic>?> signInWithGoogle() async {
    try {
      // Step 1: Sign in with Google
      final GoogleSignInAccount? account = await _googleSignIn.signIn();
      if (account == null) {
        print('User cancelled sign-in');
        return null;
      }
      
      // Step 2: Get ID token
      final GoogleSignInAuthentication auth = await account.authentication;
      final String? idToken = auth.idToken;
      
      if (idToken == null) {
        print('Failed to get ID token');
        return null;
      }
      
      // Step 3: Send ID token to backend
      final response = await http.post(
        Uri.parse('$baseUrl/auth/google/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'id_token': idToken}),
      );
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        
        // Step 4: Save the token for future API calls
        final String apiToken = data['token'];
        await _saveToken(apiToken);
        
        print('Login successful!');
        print('User: ${data['user']['email']}');
        print('Is new user: ${data['is_new_user']}');
        
        return data;
      } else {
        print('Backend error: ${response.body}');
        return null;
      }
    } catch (e) {
      print('Error: $e');
      return null;
    }
  }
  
  Future<void> _saveToken(String token) async {
    // Save to secure storage (use flutter_secure_storage or shared_preferences)
    // Example: await storage.write(key: 'api_token', value: token);
  }
  
  // Use this token for authenticated API calls
  Future<http.Response> getGames(String token) async {
    return await http.get(
      Uri.parse('https://games.agames.cv/api/games/'),
      headers: {
        'Authorization': 'Token $token',
      },
    );
  }
}
```

---

## 🔑 Using the Token for API Calls

After successful login, use the token in the `Authorization` header:

```
Authorization: Token a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

**Example API Call:**
```dart
final response = await http.get(
  Uri.parse('https://games.agames.cv/api/games/'),
  headers: {
    'Authorization': 'Token $apiToken',
  },
);
```

**cURL Example:**
```bash
curl -H "Authorization: Token a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6" \
     https://games.agames.cv/api/games/
```

---

## 📋 Configuration Checklist

### Google Cloud Console
- ✅ OAuth Client ID created
- ✅ Client ID: `your-client-id.apps.googleusercontent.com`
- ✅ Authorized JavaScript origins: `https://games.agames.cv`
- ✅ Redirect URI: `https://games.agames.cv/accounts/google/login/callback/`

### Mobile App Configuration
- [ ] Add Google Sign-In SDK to your project
- [ ] Configure with Client ID above
- [ ] Request `id_token` scope
- [ ] Send `id_token` to `https://games.agames.cv/api/users/auth/google/`
- [ ] Store returned `token` securely
- [ ] Use token in `Authorization: Token <token>` header

---

## 🧪 Testing

### Test with cURL (using a real Google ID token):
```bash
curl -X POST https://games.agames.cv/api/users/auth/google/ \
  -H "Content-Type: application/json" \
  -d '{"id_token": "YOUR_GOOGLE_ID_TOKEN_HERE"}'
```

### Test Endpoint Availability:
```bash
curl https://games.agames.cv/api/users/auth/google/
```

---

## ❌ Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `id_token is required` | Missing token in request | Send `{"id_token": "..."}` in body |
| `Invalid Google token` | Token expired or invalid | Get fresh token from Google SDK |
| `Email not verified` | Google account email unverified | Use verified Google account |
| `401 Unauthorized` (API calls) | Missing/invalid token | Check `Authorization: Token <token>` header |

---

## 🔄 Login Flow Summary

```
1. User taps "Sign in with Google" in mobile app
   ↓
2. Google Sign-In SDK shows account picker
   ↓
3. User selects Google account
   ↓
4. SDK returns authentication object with id_token
   ↓
5. App sends POST to https://games.agames.cv/api/users/auth/google/
   Body: {"id_token": "..."}
   ↓
6. Backend verifies token with Google
   ↓
7. Backend creates/updates user account
   ↓
8. Backend returns API token
   ↓
9. App saves token securely
   ↓
10. App uses token for all future API calls:
    Authorization: Token <saved_token>
```

---

## 📞 Support

**API Base URL:** `https://games.agames.cv/api/`  
**Google OAuth Endpoint:** `https://games.agames.cv/api/users/auth/google/`  
**Health Check:** `https://games.agames.cv/health/`

**Client ID:** `your-client-id.apps.googleusercontent.com`

---

**Last Updated:** December 5, 2025  
**API Version:** 1.0
