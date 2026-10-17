"""
End-to-end test for the 3 new subscription endpoints.
Runs entirely in-process (no HTTP server needed).
Uses a throw-away test user and cleans up after itself.
"""

import os
import sys
import django

os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamezone.settings')
django.setup()

from django.test.utils import setup_test_environment
setup_test_environment()

from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch
import json

User = get_user_model()

# ── helpers ────────────────────────────────────────────────────────────────────

GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def ok(msg):  print(f"  {GREEN}✅ {msg}{RESET}")
def fail(msg):print(f"  {RED}❌ {msg}{RESET}")
def sep(title=""):
    print(f"\n{BOLD}{YELLOW}{'─'*60}{RESET}")
    if title:
        print(f"{BOLD}{YELLOW}  {title}{RESET}")
        print(f"{BOLD}{YELLOW}{'─'*60}{RESET}")

FAKE_EMAIL    = "test_subscription_user@agames.test"
FAKE_EMAIL_B  = "test_device_b_user@agames.test"
FAKE_PASSWORD = "StrongPass123!"
PACKAGE_NAME  = "com.agames.play"

# ── setup ──────────────────────────────────────────────────────────────────────

def create_test_user(email):
    User.objects.filter(email=email).delete()
    u = User.objects.create_user(
        email=email,
        password=FAKE_PASSWORD,
        username=email.split('@')[0],
    )
    u.is_email_verified = True
    u.save()
    return u

# ── test blocks ────────────────────────────────────────────────────────────────

def test_login_returns_token_and_session(user):
    sep("TEST 1 – Login returns token + session_id")
    client = APIClient()
    resp = client.post('/api/users/login/', {
        'email': user.email,
        'password': FAKE_PASSWORD,
    }, format='json')
    
    data = resp.json()
    assert resp.status_code == 200, f"Login failed: {data}"
    assert 'token' in data,      "No token in response"
    assert 'session_id' in data, "No session_id in response"
    ok(f"Login succeeded. Token: {data['token'][:12]}… | Session: {data['session_id'][:8]}…")
    return data['token'], data['session_id']


def test_second_login_invalidates_first(user, token_a, session_a):
    sep("TEST 2 – Second login on Device B invalidates Device A token")
    client_b = APIClient()
    resp = client_b.post('/api/users/login/', {
        'email': user.email,
        'password': FAKE_PASSWORD,
    }, format='json')
    data_b = resp.json()
    assert resp.status_code == 200
    token_b     = data_b['token']
    session_b   = data_b['session_id']
    ok(f"Device B logged in. Token: {token_b[:12]}… | Session: {session_b[:8]}…")

    # Device A tries to use the status endpoint with old session_id
    client_a = APIClient()
    client_a.credentials(
        HTTP_AUTHORIZATION=f'Token {token_a}',
        HTTP_X_SESSION_ID=session_a,
    )
    resp_a = client_a.get('/api/users/status/')
    
    # The old token no longer exists in DB (we deleted + recreated), so it
    # should return 401 even without session_id mismatch.
    assert resp_a.status_code == 401, (
        f"Expected 401 for Device A but got {resp_a.status_code}: {resp_a.json()}"
    )
    ok("Device A got 401 (forced logout) ✓")
    return token_b, session_b


def test_status_no_premium(user, token, session_id):
    sep("TEST 3 – GET /api/users/status (user is NOT premium)")
    client = APIClient()
    client.credentials(
        HTTP_AUTHORIZATION=f'Token {token}',
        HTTP_X_SESSION_ID=session_id,
    )
    resp = client.get('/api/users/status/')
    data = resp.json()
    assert resp.status_code == 200, f"Status failed: {data}"
    assert data['is_premium'] == False
    assert data['expiration_date'] is None
    ok(f"Status: is_premium={data['is_premium']}, expiration={data['expiration_date']}")


def test_status_with_premium(user, token, session_id):
    sep("TEST 4 – GET /api/users/status (user IS premium with future expiry)")
    # Manually grant premium with future expiry
    future = timezone.now() + timedelta(days=30)
    user.is_premium = True
    user.premium_expiration = future
    user.save(update_fields=['is_premium', 'premium_expiration'])

    client = APIClient()
    client.credentials(
        HTTP_AUTHORIZATION=f'Token {token}',
        HTTP_X_SESSION_ID=session_id,
    )
    resp = client.get('/api/users/status/')
    data = resp.json()
    assert resp.status_code == 200
    assert data['is_premium'] == True
    assert data['expiration_date'] is not None
    ok(f"Status: is_premium=True, expires={data['expiration_date']}")

    # Reset for next test
    user.is_premium = False
    user.premium_expiration = None
    user.save(update_fields=['is_premium', 'premium_expiration'])


def test_premium_auto_expiry(user, token, session_id):
    sep("TEST 5 – Expired premium is auto-revoked on status check")
    # Set expiry in the past
    past = timezone.now() - timedelta(seconds=1)
    user.is_premium = True
    user.premium_expiration = past
    user.save(update_fields=['is_premium', 'premium_expiration'])

    client = APIClient()
    client.credentials(
        HTTP_AUTHORIZATION=f'Token {token}',
        HTTP_X_SESSION_ID=session_id,
    )
    resp = client.get('/api/users/status/')
    data = resp.json()
    assert resp.status_code == 200
    assert data['is_premium'] == False, "Premium should have been auto-expired"
    ok("Expired premium auto-revoked on status check ✓")

    # Reload from DB to confirm persistence
    user.refresh_from_db()
    assert user.is_premium == False
    assert user.premium_expiration is None
    ok("DB record updated: is_premium=False, premium_expiration=None ✓")


def test_google_play_verify_mock(user, token, session_id):
    sep("TEST 6 – POST /api/payments/verify (mocked Google API)")

    FAKE_TOKEN   = "fake_google_purchase_token_abc123xyz"
    PRODUCT_ID   = "agamespro_sub_1month"
    future_expiry = timezone.now() + timedelta(days=30)
    expiry_millis = int(future_expiry.timestamp() * 1000)

    mock_google_response = {
        'success': True,
        'expiry_time': future_expiry,
        'order_id': 'GPA.3313-0000-1111-22222',
        'raw': {
            'expiryTimeMillis': str(expiry_millis),
            'paymentState': 1,
            'orderId': 'GPA.3313-0000-1111-22222',
        },
        'error': None,
    }

    with patch('payments.google_play.verify_subscription', return_value=mock_google_response):
        client = APIClient()
        client.credentials(
            HTTP_AUTHORIZATION=f'Token {token}',
            HTTP_X_SESSION_ID=session_id,
        )
        resp = client.post('/api/payments/verify/', {
            'purchase_token': FAKE_TOKEN,
            'product_id': PRODUCT_ID,
        }, format='json')

    data = resp.json()
    assert resp.status_code == 200, f"Verify failed: {data}"
    assert data['is_premium'] == True
    assert data['expiration_date'] is not None
    ok(f"Purchase verified. is_premium=True, expires={data['expiration_date']}")

    # Confirm DB record
    from payments.models import GooglePlayPurchase
    purchase = GooglePlayPurchase.objects.get(purchase_token=FAKE_TOKEN)
    assert purchase.user == user
    assert purchase.product_id == PRODUCT_ID
    ok(f"GooglePlayPurchase saved. order_id={purchase.order_id}")

    # Reload user
    user.refresh_from_db()
    assert user.is_premium == True
    ok("User.is_premium=True in DB ✓")
    return FAKE_TOKEN


def test_token_reuse_fraud(user, token, session_id, used_token):
    sep("TEST 7 – Anti-fraud: same token re-used by a different user")
    # Create attacker user
    attacker = create_test_user(FAKE_EMAIL_B)
    attacker_token_obj = Token.objects.create(user=attacker)
    attacker.rotate_session()
    attacker.refresh_from_db()

    with patch('payments.google_play.verify_subscription', return_value={
        'success': True,
        'expiry_time': timezone.now() + timedelta(days=30),
        'order_id': 'GPA.3313-0000-1111-22222',
        'raw': {},
        'error': None,
    }):
        client = APIClient()
        client.credentials(
            HTTP_AUTHORIZATION=f'Token {attacker_token_obj.key}',
            HTTP_X_SESSION_ID=attacker.session_id,
        )
        resp = client.post('/api/payments/verify/', {
            'purchase_token': used_token,   # ← same token as Test 6
            'product_id': 'agamespro_sub_1month',
        }, format='json')

    data = resp.json()
    assert resp.status_code == 409, f"Expected 409 conflict, got {resp.status_code}: {data}"
    ok(f"Fraud attempt rejected with 409 Conflict ✓")
    ok(f"  Error: {data.get('error')}")

    # Attacker must still NOT be premium
    attacker.refresh_from_db()
    assert attacker.is_premium == False
    ok("Attacker is NOT premium ✓")

    # Cleanup attacker
    attacker.delete()


def test_same_user_retry(user, token, session_id, used_token):
    sep("TEST 8 – Same user retries the same token (e.g. app crash → retry)")
    with patch('payments.google_play.verify_subscription', return_value={
        'success': True,
        'expiry_time': timezone.now() + timedelta(days=30),
        'raw': {}, 'order_id': '', 'error': None,
    }):
        client = APIClient()
        client.credentials(
            HTTP_AUTHORIZATION=f'Token {token}',
            HTTP_X_SESSION_ID=session_id,
        )
        resp = client.post('/api/payments/verify/', {
            'purchase_token': used_token,
            'product_id': 'agamespro_sub_1month',
        }, format='json')

    data = resp.json()
    assert resp.status_code == 200, f"Expected 200 for retry but got {resp.status_code}: {data}"
    ok("Same user retry returns 200 (idempotent) ✓")


# ── main ───────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    sep("SUBSCRIPTION SYSTEM – END-TO-END TEST")
    print(f"  Fake user: {FAKE_EMAIL}")

    user = create_test_user(FAKE_EMAIL)

    try:
        token_a, session_a = test_login_returns_token_and_session(user)
        token_b, session_b = test_second_login_invalidates_first(user, token_a, session_a)

        # Reload user after second login (session_id may have changed in DB)
        user.refresh_from_db()

        test_status_no_premium(user, token_b, session_b)
        test_status_with_premium(user, token_b, session_b)
        test_premium_auto_expiry(user, token_b, session_b)
        used_token = test_google_play_verify_mock(user, token_b, session_b)
        test_token_reuse_fraud(user, token_b, session_b, used_token)
        test_same_user_retry(user, token_b, session_b, used_token)

        sep("ALL TESTS PASSED")
        print(f"  {GREEN}{BOLD}8/8 tests passed ✓{RESET}")

    except AssertionError as e:
        sep("TEST FAILED")
        fail(str(e))
        sys.exit(1)
    finally:
        # Cleanup
        User.objects.filter(email=FAKE_EMAIL).delete()
        User.objects.filter(email=FAKE_EMAIL_B).delete()
        print(f"\n  Cleaned up test user.\n")
