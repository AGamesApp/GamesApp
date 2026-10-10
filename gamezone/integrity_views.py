"""
Google Play Integrity API — Device Verification Endpoint
=========================================================
POST /api/verify-device/

Accepts an integrity_token from the Android app, decodes it via the
Google Play Integrity API, validates the verdict, and — if approved —
returns a signed JWT (valid 3 days) that the app attaches as
X-Device-Token on subsequent requests.

PASSIVE MODE:
  When AppSettings.device_mode_required is False, this endpoint always
  returns HTTP 200 with a valid device_token, skipping all Google verification.
"""

import json
import logging
import threading
from datetime import datetime, timedelta, timezone

import jwt
from google.oauth2 import service_account
from googleapiclient.discovery import build
from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

logger = logging.getLogger(__name__)

TARGET_IP = "197.54.40.93"

_PLAY_INTEGRITY_SCOPES = [
    "https://www.googleapis.com/auth/playintegrity",
]

_service_lock = threading.Lock()
_play_integrity_service = None

_DEVICE_MODE_CACHE_KEY = "agames:device_mode_required"
_DEVICE_MODE_CACHE_TTL = 30  # seconds


def _get_service():
    """Return a cached Play Integrity API service client (thread-safe)."""
    global _play_integrity_service
    if _play_integrity_service is not None:
        return _play_integrity_service
    with _service_lock:
        if _play_integrity_service is None:
            credentials = service_account.Credentials.from_service_account_file(
                settings.GOOGLE_CREDENTIALS_FILE,
                scopes=_PLAY_INTEGRITY_SCOPES,
            )
            _play_integrity_service = build(
                "playintegrity",
                "v1",
                credentials=credentials,
                cache_discovery=False,
            )
    return _play_integrity_service


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


def _issue_device_token(label: str = "PASSIVE") -> str:
    """Issue a signed JWT device token (used in passive mode)."""
    now = datetime.now(tz=timezone.utc)
    token_payload = {
        "sub": settings.ANDROID_PACKAGE_NAME,
        "iat": now,
        "exp": now + timedelta(days=3),
        "app_verdict": label,
        "device_verdicts": [label],
    }
    return jwt.encode(token_payload, settings.DEVICE_JWT_SECRET, algorithm="HS256")


@method_decorator(csrf_exempt, name="dispatch")
class VerifyDeviceTokenView(View):
    """
    Decode a Play Integrity token and issue a device JWT.

    When AppSettings.device_mode_required = False (PASSIVE):
      → Always returns HTTP 200 with a device_token, skip Google verification.

    When AppSettings.device_mode_required = True (REQUIRED):
      → Perform full Google Play Integrity verification.

    Expected request body (JSON):
        { "integrity_token": "<token-from-android>" }

    Success response (200):
        { "device_token": "<signed-jwt>" }

    Failure response (403):
        { "error": "<reason>" }
    """

    def post(self, request, *args, **kwargs):
        client_ip = (
            request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()
            or request.META.get('REMOTE_ADDR', 'Unknown')
        )

        # ── PASSIVE MODE: skip verification, return 200 without device token ──
        if not _is_device_mode_required():
            if client_ip == TARGET_IP:
                logger.info(
                    "Play Integrity PASSIVE MODE — skipping verification | IP: %s", client_ip
                )
            return JsonResponse({"message": "Device verification skipped (passive mode)."}, status=200)

        # ── REQUIRED MODE: full Google Play Integrity verification ──────────
        try:
            body = json.loads(request.body)
            integrity_token = body.get("integrity_token", "").strip()
        except (json.JSONDecodeError, AttributeError):
            return JsonResponse({"error": "Invalid JSON body."}, status=400)

        if not integrity_token:
            return JsonResponse({"error": "integrity_token is required."}, status=400)

        try:
            service = _get_service()
        except Exception as exc:
            if client_ip == TARGET_IP:
                logger.error("Play Integrity: failed to build API client — %s", exc)
            return JsonResponse({"error": "Server configuration error."}, status=500)

        try:
            response = (
                service.v1()
                .decodeIntegrityToken(
                    packageName=settings.ANDROID_PACKAGE_NAME,
                    body={"integrityToken": integrity_token},
                )
                .execute()
            )
        except Exception as exc:
            if client_ip == TARGET_IP:
                logger.info(
                    "Play Integrity VERIFY FAILED (decode error) — IP: %s | pkg=%s err=%s",
                    client_ip,
                    settings.ANDROID_PACKAGE_NAME,
                    exc,
                )
            return JsonResponse(
                {"error": "Failed to decode integrity token."}, status=403
            )

        payload = response.get("tokenPayloadExternal", {})
        app_integrity = payload.get("appIntegrity", {})
        device_integrity = payload.get("deviceIntegrity", {})

        app_verdict = app_integrity.get("appRecognitionVerdict", "")
        device_verdicts = device_integrity.get("deviceRecognitionVerdict", [])

        app_ok = app_verdict == "PLAY_RECOGNIZED"
        device_ok = "MEETS_DEVICE_INTEGRITY" in device_verdicts

        if not (app_ok and device_ok):
            if client_ip == TARGET_IP:
                logger.warning(
                    "Play Integrity VERIFY FAILED — IP: %s | app_ok=%s device_ok=%s app=%s device=%s pkg=%s",
                    client_ip,
                    app_ok,
                    device_ok,
                    app_verdict,
                    device_verdicts,
                    settings.ANDROID_PACKAGE_NAME,
                )
            return JsonResponse(
                {
                    "error": "Device integrity verification failed.",
                    "app_recognition_verdict": app_verdict,
                    "device_recognition_verdict": device_verdicts,
                },
                status=403,
            )

        now = datetime.now(tz=timezone.utc)
        token_payload = {
            "sub": settings.ANDROID_PACKAGE_NAME,
            "iat": now,
            "exp": now + timedelta(days=3),
            "app_verdict": app_verdict,
            "device_verdicts": device_verdicts,
        }

        try:
            device_token = jwt.encode(
                token_payload,
                settings.DEVICE_JWT_SECRET,
                algorithm="HS256",
            )
        except Exception as exc:
            if client_ip == TARGET_IP:
                logger.error("Play Integrity: JWT signing failed — %s", exc)
            return JsonResponse({"error": "Token generation error."}, status=500)

        if client_ip == TARGET_IP:
            logger.info(
                "Play Integrity VERIFY SUCCESS — IP: %s | pkg=%s app=%s device=%s",
                client_ip,
                settings.ANDROID_PACKAGE_NAME,
                app_verdict,
                device_verdicts,
            )

        return JsonResponse({"device_token": device_token})
