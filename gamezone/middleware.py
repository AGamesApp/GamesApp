"""
Device Integrity Middleware
============================
Inspects every inbound request for an ``X-Device-Token`` header.

MODE is controlled dynamically via AppSettings.device_mode_required (DB flag):
  - False (PASSIVE)  → request.is_secure_device set but NO 403 is ever returned.
                        All requests pass through regardless of token validity.
  - True  (REQUIRED) → requests without a valid token receive HTTP 403.

The mode is cached for 30 seconds to avoid a DB hit on every request.
"""

import logging
import jwt
from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse

logger = logging.getLogger(__name__)

TARGET_IP = "197.54.40.93"
_DEVICE_MODE_CACHE_KEY = "agames:device_mode_required"
_DEVICE_MODE_CACHE_TTL = 30  # seconds


def _is_device_mode_required() -> bool:
    """Read device_mode_required from AppSettings (cached 30s)."""
    cached = cache.get(_DEVICE_MODE_CACHE_KEY)
    if cached is not None:
        return cached
    try:
        from games.models import AppSettings
        obj = AppSettings.objects.only("device_mode_required").get(pk=1)
        result = bool(obj.device_mode_required)
    except Exception:
        result = False  # safe default: passive
    cache.set(_DEVICE_MODE_CACHE_KEY, result, _DEVICE_MODE_CACHE_TTL)
    return result


class DeviceIntegrityMiddleware:
    """JWT inspection middleware for Google Play Integrity device tokens.

    Mode is controlled by AppSettings.device_mode_required:
    - PASSIVE  (False): observe only, never block.
    - REQUIRED (True):  block requests without a valid device token.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.is_secure_device = self._verify_device_token(request)
        if not request.is_secure_device and _is_device_mode_required():
            return JsonResponse({"error": "Device integrity token required."}, status=403)
        return self.get_response(request)

    # ── Internal helpers ───────────────────────────────────────────────────

    def _verify_device_token(self, request) -> bool:
        """
        Return True only when the X-Device-Token header contains a JWT that
        was signed by DEVICE_JWT_SECRET and has not expired.
        """
        # 1. List of paths to exclude entirely
        excluded_paths = (
            '/',
            '/health/',
            '/privacy/',
            '/go/',
            '/go',
            '/game/',
            '/game',
            '/.well-known/assetlinks.json',
            '/api/app_details/',
            '/api/app-details/',
            '/api/verify-device/',
        )

        # 2. List of prefixes to exclude entirely
        excluded_prefixes = (
            '/customadmin/',
            '/accounts/',
            '/api/schema/',
            '/api/docs/',
            '/admin/',
            '/go',
            '/game',
        )

        if request.path in excluded_paths or request.path.startswith(excluded_prefixes):
            return True

        raw_token = request.META.get("HTTP_X_DEVICE_TOKEN", "").strip()

        user_id = getattr(request.user, 'id', 'Anonymous') if hasattr(request, 'user') else 'Anonymous'
        ip = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() or request.META.get('REMOTE_ADDR', 'Unknown')
        path = request.path

        if not raw_token:
            if ip == TARGET_IP:
                logger.info(f"[DEVICE_TOKEN_MISSING] User: {user_id} | IP: {ip} | Path: {path}")
            return False

        secret = getattr(settings, "DEVICE_JWT_SECRET", None)
        if not secret:
            logger.error("DeviceIntegrityMiddleware: DEVICE_JWT_SECRET is not configured.")
            return False

        try:
            jwt.decode(
                raw_token,
                secret,
                algorithms=["HS256"],
                options={"require": ["exp", "iat", "sub"]},
            )
            if ip == TARGET_IP:
                logger.info(f"[DEVICE_TOKEN_SUCCESS] User: {user_id} | IP: {ip} | Path: {path}")
            return True

        except jwt.ExpiredSignatureError:
            if ip == TARGET_IP:
                logger.info(f"[DEVICE_TOKEN_EXPIRED] User: {user_id} | IP: {ip} | Path: {path}")
        except jwt.InvalidTokenError:
            if ip == TARGET_IP:
                logger.info(f"[DEVICE_TOKEN_INVALID] User: {user_id} | IP: {ip} | Path: {path}")
        except Exception:
            if ip == TARGET_IP:
                logger.info(f"[DEVICE_TOKEN_ERROR] User: {user_id} | IP: {ip} | Path: {path}")

        return False
