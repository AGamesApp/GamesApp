"""
Google Play Developer API v2 integration for subscription verification.

Uses the service account credentials (same serviceAccountKey.json used for Firebase)
to call the Google Play Developer API v2 (purchases/subscriptionsv2/tokens/{token}).

Supports Billing Library 5, 6, 7, 8+.
"""

import logging
from datetime import datetime, timedelta, timezone as dt_timezone
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger('payments')

# States that represent an active / still-usable subscription in v2 API
VALID_SUBSCRIPTION_STATES = {
    'SUBSCRIPTION_STATE_ACTIVE',
    'SUBSCRIPTION_STATE_CANCELED',         # cancelled but valid until expiry date
    'SUBSCRIPTION_STATE_IN_GRACE_PERIOD',  # payment failed, grace period still active
}

# Fallback expiry days if Google does not return an expiryTime
PRODUCT_DURATIONS = {
    'agamespro_sub_1month':  30,
    'agamespro_sub_3months': 90,
    'agamespro_sub_6months': 180,
}


def _get_play_service():
    """
    Build and return a Google Play Developer API service object.
    Re-uses the Firebase service account key which must also have
    Google Play Developer API access enabled.
    """
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        credentials = service_account.Credentials.from_service_account_file(
            settings.FIREBASE_CREDENTIALS_PATH,
            scopes=['https://www.googleapis.com/auth/androidpublisher'],
        )
        service = build('androidpublisher', 'v3', credentials=credentials, cache_discovery=False)
        return service
    except Exception as e:
        logger.error(f"Failed to build Google Play service: {e}")
        return None


def _parse_iso_expiry(expiry_str: str):
    """Parse ISO 8601 expiry string returned by Google API v2 into a UTC-aware datetime."""
    if not expiry_str:
        return None
    try:
        # Google returns e.g. "2026-04-10T12:00:00.000000Z"
        # Replace trailing Z so Python 3.7+ fromisoformat() can parse it
        return datetime.fromisoformat(expiry_str.replace('Z', '+00:00'))
    except Exception:
        return None


def verify_subscription(package_name: str, product_id: str, purchase_token: str) -> dict:
    """
    Verify a Google Play subscription purchase token using API v2.

    API v2 endpoint: GET androidpublisher/v3/applications/{pkg}/purchases/subscriptionsv2/tokens/{token}
    Works with all Billing Library versions (5, 6, 7, 8+).

    Returns a dict with:
        success    (bool)
        expiry_time (datetime | None)  – UTC-aware
        order_id   (str)
        product_id (str)               – as confirmed by Google (for cross-validation)
        raw        (dict)              – full API response
        error      (str | None)
    """
    service = _get_play_service()
    if service is None:
        return {
            'success': False,
            'expiry_time': None,
            'order_id': '',
            'product_id': product_id,
            'raw': {},
            'error': 'Could not initialise Google Play API service',
        }

    try:
        # ---- API v2: no subscriptionId needed, just the token ----
        result = (
            service.purchases()
            .subscriptionsv2()
            .get(
                packageName=package_name,
                token=purchase_token,
            )
            .execute()
        )

        # ---- Parse line items (v2 response structure) ----
        line_items = result.get('lineItems', [])
        if not line_items:
            return {
                'success': False,
                'expiry_time': None,
                'order_id': '',
                'product_id': product_id,
                'raw': result,
                'error': 'No subscription line items in Google Play response',
            }

        item = line_items[0]
        returned_product_id = item.get('productId', product_id)
        expiry_dt = _parse_iso_expiry(item.get('expiryTime', ''))

        # ---- Fallback: calculate expiry from product if API omits it ----
        if expiry_dt is None:
            days = PRODUCT_DURATIONS.get(product_id, 30)
            expiry_dt = timezone.now() + timedelta(days=days)
            logger.warning(
                f"No expiryTime in Google response for {product_id}; "
                f"falling back to calculated +{days}d expiry"
            )

        subscription_state = result.get('subscriptionState', '')
        order_id = result.get('latestOrderId', '')

        is_valid = (
            subscription_state in VALID_SUBSCRIPTION_STATES
            and expiry_dt > timezone.now()
        )

        return {
            'success': is_valid,
            'expiry_time': expiry_dt,
            'order_id': order_id,
            'product_id': returned_product_id,
            'raw': result,
            'error': None if is_valid else f'Subscription not active (state: {subscription_state})',
        }

    except Exception as e:
        err_str = str(e)
        logger.error(f"Google Play v2 verification failed: {err_str}")

        # Classify the error so the caller can choose the right HTTP status code
        if '400' in err_str or 'invalid' in err_str.lower():
            error_msg = 'Invalid purchase token'
        elif '401' in err_str or 'insufficient permissions' in err_str.lower():
            error_msg = 'Google Play API permission error — contact support'
        elif '404' in err_str:
            error_msg = 'Purchase token not found in Google Play'
        else:
            error_msg = 'Google Play verification failed'

        return {
            'success': False,
            'expiry_time': None,
            'order_id': '',
            'product_id': product_id,
            'raw': {},
            'error': error_msg,
        }
