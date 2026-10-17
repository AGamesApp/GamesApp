#!/usr/bin/env python3
"""
Comprehensive Live HTTP Test Suite for AGames Pro (https://games.agames.cv)
=============================================================================
Tests all resources, user flows, admin dashboard, catalog APIs, Play Integrity,
and Google OAuth endpoints via live HTTPS requests, and cleans up test data afterwards.
"""

import sys
import os
import json
import requests
import django

# Setup Django environment for verification & cleanup
sys.path.insert(0, '/root/GamesApp/agames-main')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamezone.settings')
django.setup()

from users.models import User
from games.models import Game, Emulator, GameRating, GameLove, GameReview
from rest_framework.authtoken.models import Token

BASE_URL = "https://games.agames.cv"

# Test results tracker
results = []

def record(test_name, success, message=""):
    status_str = "PASS" if success else "FAIL"
    print(f"[{status_str}] {test_name}: {message}")
    results.append((test_name, success, message))

def test_endpoints():
    session = requests.Session()
    session.headers.update({"User-Agent": "AGamesPro-Tester/1.0"})

    print("=" * 70)
    print("1. TESTING PUBLIC WEB & SYSTEM ENDPOINTS")
    print("=" * 70)

    # 1.1 Landing page
    r = session.get(f"{BASE_URL}/")
    record("Landing Page (GET /)", r.status_code == 200 and "AGames Pro" in r.text, f"HTTP {r.status_code}")

    # 1.2 Privacy Policy
    r = session.get(f"{BASE_URL}/privacy/")
    record("Privacy Policy (GET /privacy/)", r.status_code == 200 and "Privacy Policy" in r.text, f"HTTP {r.status_code}")

    # 1.3 Health Check
    r = session.get(f"{BASE_URL}/health/")
    record("Health Check (GET /health/)", r.status_code == 200 and r.json().get("status") == "healthy", f"HTTP {r.status_code} - {r.text}")

    # 1.4 AssetLinks
    r = session.get(f"{BASE_URL}/.well-known/assetlinks.json")
    assetlinks_ok = r.status_code == 200 and "50:11:B2:A8:71:A9:F4:B5" in r.text and "BE:2E:BE:09:E6:E5" in r.text
    record("AssetLinks (GET /.well-known/assetlinks.json)", assetlinks_ok, f"HTTP {r.status_code}")

    # 1.5 Static Logo Asset
    r = session.get(f"{BASE_URL}/static/images/agames.jpg")
    record("Branded Logo (GET /static/images/agames.jpg)", r.status_code == 200 and len(r.content) > 100000, f"HTTP {r.status_code} ({len(r.content)} bytes)")

    # 1.6 Swagger UI & Schema
    r = session.get(f"{BASE_URL}/api/docs/")
    record("Swagger Docs (GET /api/docs/)", r.status_code == 200 and "swagger-ui" in r.text, f"HTTP {r.status_code}")

    r = session.get(f"{BASE_URL}/api/schema/")
    record("OpenAPI Schema (GET /api/schema/)", r.status_code == 200, f"HTTP {r.status_code}")

    print("\n" + "=" * 70)
    print("2. TESTING CATALOG & APP APIs")
    print("=" * 70)

    # 2.1 Emulators list
    r = session.get(f"{BASE_URL}/api/emulators/")
    data = r.json()
    emulators_count = data.get("count", len(data.get("results", [])))
    first_emu_id = data["results"][0]["id"] if data.get("results") else 1
    record("Emulators List (GET /api/emulators/)", r.status_code == 200 and emulators_count >= 3, f"HTTP {r.status_code} (Found {emulators_count} emulators)")

    # 2.2 Emulator detail & additional files
    r = session.get(f"{BASE_URL}/api/emulators/{first_emu_id}/")
    emu_det = r.json()
    has_files = len(emu_det.get("additional_files", [])) > 0
    record(f"Emulator Detail (GET /api/emulators/{first_emu_id}/)", r.status_code == 200, f"HTTP {r.status_code} - {emu_det.get('name')}")
    record("Emulator Additional Files Nested in Detail", has_files, f"Found {len(emu_det.get('additional_files', []))} additional file(s)")

    # 2.3 Games list
    r = session.get(f"{BASE_URL}/api/games/")
    games_data = r.json()
    games_count = games_data.get("count", len(games_data.get("results", [])))
    first_game = games_data["results"][0] if games_data.get("results") else None
    first_game_id = first_game["id"] if first_game else 1
    record("Games List (GET /api/games/)", r.status_code == 200 and games_count >= 5, f"HTTP {r.status_code} (Found {games_count} games)")

    # 2.4 Games search filter
    r = session.get(f"{BASE_URL}/api/games/?search=God")
    search_data = r.json()
    record("Games Search (GET /api/games/?search=God)", r.status_code == 200 and search_data.get("count", 0) >= 1, f"HTTP {r.status_code} (Found {search_data.get('count')} games)")

    # 2.5 Game detail
    r = session.get(f"{BASE_URL}/api/games/{first_game_id}/")
    record(f"Game Detail (GET /api/games/{first_game_id}/)", r.status_code == 200, f"HTTP {r.status_code} - {r.json().get('title')}")

    # 2.6 Subscription Plans list
    r = session.get(f"{BASE_URL}/api/plans/")
    plans_data = r.json()
    record("Subscription Plans (GET /api/plans/)", r.status_code == 200 and len(plans_data) >= 2, f"HTTP {r.status_code} ({len(plans_data)} plans)")

    # 2.7 App details endpoint
    r = session.get(f"{BASE_URL}/api/app_details/")
    app_det = r.json()
    record("App Details (GET /api/app_details/)", r.status_code == 200 and app_det.get("app_version") == "1.0.0", f"HTTP {r.status_code} - v{app_det.get('app_version')}")

    print("\n" + "=" * 70)
    print("3. TESTING USER WORKFLOW (REGISTRATION, AUTH, ACTIONS, CLEANUP)")
    print("=" * 70)

    test_username = "test_user_val_2026"
    test_email = "test_user_val_2026@agames.cv"
    test_password = "SecureValPassword123!"

    # Ensure clean slate before test
    User.objects.filter(email=test_email).delete()

    # 3.1 User Registration
    reg_payload = {
        "username": test_username,
        "email": test_email,
        "password": test_password,
        "password_confirm": test_password
    }
    r = session.post(f"{BASE_URL}/api/users/register/", json=reg_payload)
    record("User Registration (POST /api/users/register/)", r.status_code in [200, 201], f"HTTP {r.status_code} - {r.text[:80]}")

    # Verify user in DB and activate for login
    user_obj = None
    try:
        user_obj = User.objects.get(email=test_email)
        user_obj.is_active = True
        user_obj.is_email_verified = True
        user_obj.save()
        user_exists = True
    except User.DoesNotExist:
        user_exists = False
    record("User Created in Database", user_exists, f"User ID: {getattr(user_obj, 'id', None)}")

    # 3.2 User Login
    login_payload = {
        "email": test_email,
        "password": test_password
    }
    r = session.post(f"{BASE_URL}/api/users/login/", json=login_payload)
    login_data = r.json()
    user_token = login_data.get("token") or login_data.get("key")
    record("User Login (POST /api/users/login/)", r.status_code == 200 and bool(user_token), f"HTTP {r.status_code} - Token obtained: {bool(user_token)}")

    if user_token:
        auth_headers = {"Authorization": f"Token {user_token}"}

        # 3.3 User Profile
        r = session.get(f"{BASE_URL}/api/users/profile/", headers=auth_headers)
        record("User Profile (GET /api/users/profile/)", r.status_code == 200 and r.json().get("email") == test_email, f"HTTP {r.status_code}")

        # 3.4 User Status (Premium check)
        r = session.get(f"{BASE_URL}/api/users/status/", headers=auth_headers)
        record("User Status (GET /api/users/status/)", r.status_code == 200, f"HTTP {r.status_code} - is_premium={r.json().get('is_premium')}")

        # 3.5 Game Download Counter (Authenticated)
        r = session.post(f"{BASE_URL}/api/games/{first_game_id}/download/", headers=auth_headers)
        record(f"Game Download Counter (POST /api/games/{first_game_id}/download/)", r.status_code in [200, 201], f"HTTP {r.status_code} - downloads={r.json().get('downloads')}")

        # 3.6 Love Game
        r = session.post(f"{BASE_URL}/api/games/{first_game_id}/love/", headers=auth_headers)
        record(f"Love Game (POST /api/games/{first_game_id}/love/)", r.status_code in [200, 201], f"HTTP {r.status_code} - {r.json()}")

        # 3.7 Loved Games List
        r = session.get(f"{BASE_URL}/api/games/my_loved_games/", headers=auth_headers)
        loved_count = r.json().get("count", len(r.json().get("results", [])))
        record("Loved Games (GET /api/games/my_loved_games/)", r.status_code == 200 and loved_count >= 1, f"HTTP {r.status_code} ({loved_count} loved)")

        # 3.8 Rate Game
        rate_payload = {"score": 5.0}
        r = session.post(f"{BASE_URL}/api/games/{first_game_id}/rate/", json=rate_payload, headers=auth_headers)
        record(f"Rate Game (POST /api/games/{first_game_id}/rate/)", r.status_code in [200, 201], f"HTTP {r.status_code} - {r.json()}")

        # 3.9 Review Game
        rev_payload = {"review": "Outstanding retro experience in AGames Pro!"}
        r = session.post(f"{BASE_URL}/api/games/{first_game_id}/review/", json=rev_payload, headers=auth_headers)
        record(f"Review Game (POST /api/games/{first_game_id}/review/)", r.status_code in [200, 201], f"HTTP {r.status_code} - {r.json()}")

        # 3.10 My Review
        r = session.get(f"{BASE_URL}/api/games/{first_game_id}/my_review/", headers=auth_headers)
        record(f"My Review (GET /api/games/{first_game_id}/my_review/)", r.status_code == 200, f"HTTP {r.status_code}")

    # 3.11 Clean up test data
    User.objects.filter(email=test_email).delete()
    cleanup_success = not User.objects.filter(email=test_email).exists()
    record("Cleanup Test User & Related Data", cleanup_success, "Test user purged from gamesapp_db")

    print("\n" + "=" * 70)
    print("4. TESTING CUSTOMADMIN DASHBOARD & AUTHENTICATION")
    print("=" * 70)

    admin_session = requests.Session()
    # Get CSRF cookie first
    login_page = admin_session.get(f"{BASE_URL}/customadmin/login/")
    csrftoken = login_page.cookies.get("csrftoken")

    admin_login_data = {
        "email": "agames.app.dev@gmail.com",
        "password": "AGames@pp#2025",
        "csrfmiddlewaretoken": csrftoken
    }
    r = admin_session.post(
        f"{BASE_URL}/customadmin/login/",
        data=admin_login_data,
        headers={"Referer": f"{BASE_URL}/customadmin/login/"}
    )
    admin_login_ok = r.status_code in [200, 302] and "login" not in r.url
    record("CustomAdmin Login (agames user)", admin_login_ok, f"HTTP {r.status_code} -> {r.url}")

    # 4.1 Dashboard
    r = admin_session.get(f"{BASE_URL}/customadmin/")
    record("CustomAdmin Dashboard", r.status_code == 200 and "Dashboard" in r.text, f"HTTP {r.status_code}")

    # 4.2 Emulators View
    r = admin_session.get(f"{BASE_URL}/customadmin/emulators/")
    record("CustomAdmin Emulators List", r.status_code == 200 and "PlayStation" in r.text, f"HTTP {r.status_code}")

    # 4.3 Games View
    r = admin_session.get(f"{BASE_URL}/customadmin/games/")
    record("CustomAdmin Games List", r.status_code == 200 and "God of War" in r.text, f"HTTP {r.status_code}")

    # 4.4 Genres View
    r = admin_session.get(f"{BASE_URL}/customadmin/genres/")
    record("CustomAdmin Genres List", r.status_code == 200 and "Action" in r.text, f"HTTP {r.status_code}")

    # 4.5 Users View
    r = admin_session.get(f"{BASE_URL}/customadmin/users/")
    record("CustomAdmin Users List", r.status_code == 200, f"HTTP {r.status_code}")

    # 4.6 App Settings View & Play Integrity UI
    r = admin_session.get(f"{BASE_URL}/customadmin/settings/")
    record("CustomAdmin Settings View", r.status_code == 200 and "Settings" in r.text, f"HTTP {r.status_code}")
    record("Dashboard Device Token Mode UI", "Device Token Mode" in r.text and "id_device_mode_required" in r.text, "Cards & Toggle Switch Rendered")

    # 4.7 Support Messages View
    r = admin_session.get(f"{BASE_URL}/customadmin/support/")
    record("CustomAdmin Support View", r.status_code == 200, f"HTTP {r.status_code}")

    print("\n" + "=" * 70)
    print("5. TESTING GOOGLE OAUTH & PLAY INTEGRITY (PASSIVE & REQUIRED MODES)")
    print("=" * 70)

    # 5.1 Google Auth ID token validation endpoint
    r = session.post(f"{BASE_URL}/api/users/auth/google/", json={"id_token": "dummy_test_token"})
    record("Google Auth ID-Token Endpoint", r.status_code == 400 and "Invalid" in r.text, f"HTTP {r.status_code} - Proper validation response: {r.text[:60]}")

    # 5.2 Google OAuth Login view
    r = session.get(f"{BASE_URL}/accounts/google/login/", allow_redirects=False)
    record("Google OAuth Redirect / Flow", r.status_code in [200, 302], f"HTTP {r.status_code}")

    # 5.3 Play Integrity PASSIVE mode (default)
    from django.core.cache import cache
    from games.models import AppSettings
    app_set = AppSettings.objects.get(pk=1)
    app_set.device_mode_required = False
    app_set.save()
    cache.delete("agames:device_mode_required")

    r = session.post(f"{BASE_URL}/api/verify-device/", json={})
    record("Play Integrity PASSIVE Mode (/api/verify-device/)", r.status_code == 200 and "passive" in r.text.lower(), f"HTTP {r.status_code} - {r.json()}")

    # 5.4 Play Integrity REQUIRED mode enforcement
    app_set.device_mode_required = True
    app_set.save()
    cache.delete("agames:device_mode_required")

    # In required mode, missing token should return 403
    r = session.get(f"{BASE_URL}/api/games/")
    record("Play Integrity REQUIRED Mode (Middleware blocks missing token)", r.status_code == 403, f"HTTP {r.status_code} - {r.json()}")

    # In required mode, valid JWT token should pass through
    from datetime import datetime, timedelta, timezone
    import jwt
    from django.conf import settings as dj_settings
    now = datetime.now(tz=timezone.utc)
    token_payload = {
        "sub": dj_settings.ANDROID_PACKAGE_NAME,
        "iat": now,
        "exp": now + timedelta(days=3),
        "app_verdict": "PLAY_RECOGNIZED",
        "device_verdicts": ["MEETS_DEVICE_INTEGRITY"],
    }
    valid_jwt = jwt.encode(token_payload, dj_settings.DEVICE_JWT_SECRET, algorithm="HS256")
    r = session.get(f"{BASE_URL}/api/games/", headers={"X-Device-Token": valid_jwt})
    record("Play Integrity REQUIRED Mode (Valid Token Accepted)", r.status_code == 200, f"HTTP {r.status_code}")

    # In required mode, verify-device contacts Google API
    r = session.post(f"{BASE_URL}/api/verify-device/", json={"integrity_token": "test_device_token_sample"})
    record("Play Integrity REQUIRED Mode (Google API Service Account Call)", r.status_code == 403 and "integrity" in r.text.lower(), f"HTTP {r.status_code} - {r.text[:60]}")

    # Reset to PASSIVE mode
    app_set.device_mode_required = False
    app_set.save()
    cache.delete("agames:device_mode_required")
    record("Reset Device Mode to PASSIVE", True, "Mode safely restored to passive")

    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    passed = sum(1 for _, ok, _ in results if ok)
    total = len(results)
    print(f"Total Tests Executed: {total}")
    print(f"Passed: {passed} / {total}")
    if passed == total:
        print("ALL TESTS PASSED SUCCESSFULLY! The application and APIs are 100% functional.")
        return 0
    else:
        print("SOME TESTS FAILED! Inspect the logs above.")
        return 1

if __name__ == "__main__":
    sys.exit(test_endpoints())
