"""
Device Integrity Middleware
============================
Inspects every inbound request for an ``X-Device-Token`` header.

ZERO-DOWNTIME DESIGN (passive / observation-only)
--------------------------------------------------
* If the header is present and the JWT is valid  → request.is_secure_device = True
* If the header is missing, expired, or invalid  → request.is_secure_device = False
* The middleware NEVER returns an HTTP error response.
* self.get_response(request) is ALWAYS called, so older app versions that
  do not send the header continue to function normally.
"""

import logging
import jwt
from django.conf import settings
from django.http import JsonResponse

# Route these logs directly to logs/security.log based on your settings.py
logger = logging.getLogger(__name__)

class DeviceIntegrityMiddleware:
    """Passive JWT inspection middleware for Google Play Integrity device tokens."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.is_secure_device = self._verify_device_token(request)
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
            '/.well-known/assetlinks.json',
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
        )

        if request.path in excluded_paths or request.path.startswith(excluded_prefixes):
            return True

        raw_token = request.META.get("HTTP_X_DEVICE_TOKEN", "").strip()

        # Extract identifying details for logging
        user_id = getattr(request.user, 'id', 'Anonymous') if hasattr(request, 'user') else 'Anonymous'
        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', 'Unknown'))
        path = request.path

        if not raw_token:
            # logger.warning(f"[DEVICE_TOKEN_MISSING] User: {user_id} | IP: {ip} | Path: {path}")
            return False

        secret = getattr(settings, "DEVICE_JWT_SECRET", None)
        if not secret:
            # logger.error("DeviceIntegrityMiddleware: DEVICE_JWT_SECRET is not configured.")
            return False

        try:
            jwt.decode(
                raw_token,
                secret,
                algorithms=["HS256"],
                options={"require": ["exp", "iat", "sub"]},
            )
            # logger.info(f"[DEVICE_TOKEN_SUCCESS] User: {user_id} | IP: {ip} | Path: {path}")
            return True

        except jwt.ExpiredSignatureError:
            # logger.info(f"[DEVICE_TOKEN_EXPIRED] User: {user_id} | IP: {ip} | Path: {path}")
            pass
        except jwt.InvalidTokenError as exc:
            # logger.info(f"[DEVICE_TOKEN_INVALID] User: {user_id} | IP: {ip} | Path: {path}")
            pass
        except Exception as exc:
            # logger.info(f"[DEVICE_TOKEN_ERROR] User: {user_id} | IP: {ip} | Path: {path}")
            pass

        return False
