#!/usr/bin/env python3
"""
Google Play Purchase Verification Test
=======================================
Usage:
  # Test API connectivity only (no real token needed):
  python test_google_play_verify.py

  # Test with a real purchase token from the app:
  python test_google_play_verify.py <purchase_token> [product_id]

  Example:
  python test_google_play_verify.py "AEuhp4A..." agamespro_sub_1month

Results:
  ✅ CONNECTED  = API access works, fake token rejected as expected
  ✅ VERIFIED   = Real token is valid, subscription is active
  ❌ EXPIRED    = Real token found but subscription has expired
  ❌ NO ACCESS  = Service account not linked in Play Console
  ❌ API OFF    = Google Play Developer API not enabled
"""

import sys
import os
import json
import django
from datetime import datetime, timezone

# ── Django setup ────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamezone.settings')
django.setup()

from django.conf import settings
from google.oauth2 import service_account
from googleapiclient.discovery import build

# ── Config ───────────────────────────────────────────────────────────────────
KEY_FILE     = getattr(settings, 'FIREBASE_CREDENTIALS_PATH', os.path.join(BASE_DIR, 'serviceAccountKey.json'))
PACKAGE_NAME = getattr(settings, 'GOOGLE_PLAY_PACKAGE_NAME', 'com.agames.play')
PRODUCTS     = ['agamespro_sub_1month', 'agamespro_sub_3months', 'agamespro_sub_6months']

# ── Build service ─────────────────────────────────────────────────────────────
def get_service():
    creds = service_account.Credentials.from_service_account_file(
        KEY_FILE,
        scopes=['https://www.googleapis.com/auth/androidpublisher'],
    )
    return build('androidpublisher', 'v3', credentials=creds, cache_discovery=False)


def classify_error(err: str) -> str:
    e = err.lower()
    if 'invalid value' in e or ('invalid' in e and '400' in err):
        return 'INVALID_TOKEN'
    if 'insufficient permissions' in e or '401' in err:
        return 'NO_ACCESS'
    if 'has not been used' in e or 'disabled' in e:
        return 'API_DISABLED'
    if 'not found' in e or '404' in err:
        return 'NOT_FOUND'
    return 'UNKNOWN'


# ── Connectivity test using API v2 (fake token) ───────────────────────────────
def test_connectivity(service):
    print(f"\n{'='*60}")
    print(f"  CONNECTIVITY TEST  (API v2 — subscriptionsv2)")
    print(f"  Package : {PACKAGE_NAME}")
    print(f"  Key file: {KEY_FILE}")
    print(f"{'='*60}")

    all_ok = True
    # v2 endpoint: no subscriptionId — just token; test once, not per product
    try:
        service.purchases().subscriptionsv2().get(
            packageName=PACKAGE_NAME,
            token='fake_connectivity_test_token',
        ).execute()
        print(f"  UNEXPECTED SUCCESS with fake token")
        all_ok = False
    except Exception as e:
        kind = classify_error(str(e))
        if kind == 'INVALID_TOKEN':
            print(f"  ✅ CONNECTED — API v2 reachable, fake token rejected correctly")
            for p in PRODUCTS:
                print(f"  [{p}]  ✅ Ready")
        elif kind == 'NO_ACCESS':
            print(f"  ❌ NO ACCESS — service account not linked in Play Console")
            all_ok = False
        elif kind == 'API_DISABLED':
            print(f"  ❌ API DISABLED — enable at console.developers.google.com")
            all_ok = False
        else:
            print(f"  ❌ ERROR: {str(e)[:200]}")
            all_ok = False

    print()
    if all_ok:
        print("  ✅ All products: API access confirmed. Ready for real purchase tokens.")
    else:
        print("  ❌ Fix the errors above before going live.")
    print()


# ── Real token test using API v2 ──────────────────────────────────────────────
def test_real_token(service, token: str, product_id: str = None):
    print(f"\n{'='*60}")
    print(f"  REAL TOKEN TEST  (API v2)")
    print(f"  Token   : {token[:40]}...")
    print(f"{'='*60}")

    try:
        # v2: no subscriptionId — token alone identifies the subscription
        result = service.purchases().subscriptionsv2().get(
            packageName=PACKAGE_NAME,
            token=token,
        ).execute()

        line_items  = result.get('lineItems', [])
        sub_state   = result.get('subscriptionState', 'UNKNOWN')
        order_id    = result.get('latestOrderId', 'N/A')

        if not line_items:
            print(f"  ❌ No line items in response")
            return

        item            = line_items[0]
        returned_product = item.get('productId', 'N/A')
        expiry_str       = item.get('expiryTime', '')
        auto_renew       = item.get('autoRenewingPlan', {}).get('autoRenewEnabled', False)

        # Parse expiry
        expiry_dt = None
        if expiry_str:
            from datetime import datetime
            expiry_dt = datetime.fromisoformat(expiry_str.replace('Z', '+00:00'))

        ACTIVE_STATES = {'SUBSCRIPTION_STATE_ACTIVE', 'SUBSCRIPTION_STATE_CANCELED',
                         'SUBSCRIPTION_STATE_IN_GRACE_PERIOD'}
        is_active = sub_state in ACTIVE_STATES and expiry_dt and expiry_dt > datetime.now(tz=expiry_dt.tzinfo)

        # Cross-validate product_id if caller specified one
        if product_id and returned_product != product_id:
            print(f"  ⚠️  Product mismatch: sent '{product_id}', Google says '{returned_product}'")

        status_str = "✅ ACTIVE" if is_active else "❌ EXPIRED/INVALID"
        print(f"\n  Product      : {returned_product}  {status_str}")
        print(f"  State        : {sub_state}")
        print(f"  Order ID     : {order_id}")
        print(f"  Expires      : {expiry_dt.strftime('%Y-%m-%d %H:%M:%S UTC') if expiry_dt else 'N/A'}")
        print(f"  Auto-renew   : {auto_renew}")

    except Exception as e:
        kind = classify_error(str(e))
        if kind == 'INVALID_TOKEN':
            print(f"  ❌ INVALID TOKEN — token does not exist or has been consumed")
        elif kind == 'NO_ACCESS':
            print(f"  ❌ NO ACCESS — service account not linked in Play Console")
        else:
            print(f"  ❌ ERROR: {str(e)[:300]}")
    print()


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print(f"\nGoogle Play Verification Test")
    print(f"Service account : ", end='')
    try:
        with open(KEY_FILE) as f:
            info = json.load(f)
        print(info['client_email'])
        print(f"Project         : {info['project_id']}")
    except Exception as e:
        print(f"ERROR reading key file: {e}")
        sys.exit(1)

    try:
        service = get_service()
    except Exception as e:
        print(f"\n❌ Failed to build API service: {e}")
        sys.exit(1)

    if len(sys.argv) >= 2:
        purchase_token = sys.argv[1]
        product_id     = sys.argv[2] if len(sys.argv) >= 3 else None
        test_real_token(service, purchase_token, product_id)
    else:
        test_connectivity(service)
