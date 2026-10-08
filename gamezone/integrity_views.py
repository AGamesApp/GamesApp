"""
Google Play Integrity API — Device Verification Endpoint
=========================================================
POST /api/verify-device/

Accepts an integrity_token from the Android app, decodes it via the
Google Play Integrity API, validates the verdict, and — if approved —
returns a signed JWT (valid 3 days) that the app attaches as
X-Device-Token on subsequent requests.
"""

import json
import logging
from datetime import datetime, timedelta, timezone

import jwt
from google.oauth2 import service_account
from googleapiclient.discovery import build
from django.conf import settings
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

logger = logging.getLogger(__name__)

_PLAY_INTEGRITY_SCOPES = [
    "https://www.googleapis.com/auth/playintegrity",
]


@method_decorator(csrf_exempt, name="dispatch")
class VerifyDeviceTokenView(View):
    """
    Decode a Play Integrity token and issue a device JWT.

    Expected request body (JSON):
        { "integrity_token": "<token-from-android>" }

    Success response (200):
        { "device_token": "<signed-jwt>" }

    Failure response (403):
        { "error": "<reason>" }
    """

    def post(self, request, *args, **kwargs):
        # ── 1. Parse request body ────────────────────────────────────────
        try:
            body = json.loads(request.body)
            integrity_token = body.get("integrity_token", "").strip()
        except (json.JSONDecodeError, AttributeError):
            return JsonResponse({"error": "Invalid JSON body."}, status=400)

        if not integrity_token:
            return JsonResponse({"error": "integrity_token is required."}, status=400)

        # ── 2. Build authenticated Google API client ─────────────────────
        try:
            credentials = service_account.Credentials.from_service_account_file(
                settings.GOOGLE_CREDENTIALS_FILE,
                scopes=_PLAY_INTEGRITY_SCOPES,
            )
            service = build(
                "playintegrity",
                "v1",
                credentials=credentials,
                cache_discovery=False,
            )
        except Exception as exc:
            # logger.error("Play Integrity: failed to build API client — %s", exc)
            return JsonResponse({"error": "Server configuration error."}, status=500)

        # ── 3. Decode the integrity token via Google ─────────────────────
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
            # logger.warning(
            #     "Play Integrity: decodeIntegrityToken failed for package=%s — %s",
            #     settings.ANDROID_PACKAGE_NAME,
            #     exc,
            # )
            return JsonResponse(
                {"error": "Failed to decode integrity token."}, status=403
            )

        # ── 4. Extract verdict payload ───────────────────────────────────
        payload = response.get("tokenPayloadExternal", {})
        app_integrity = payload.get("appIntegrity", {})
        device_integrity = payload.get("deviceIntegrity", {})

        app_verdict = app_integrity.get("appRecognitionVerdict", "")
        device_verdicts = device_integrity.get("deviceRecognitionVerdict", [])

        # logger.info(
        #     "Play Integrity verdict — app=%s device=%s pkg=%s",
        #     app_verdict,
        #     device_verdicts,
        #     settings.ANDROID_PACKAGE_NAME,
        # )

        # ── 5. Enforce strict integrity requirements ─────────────────────
        app_ok = app_verdict == "PLAY_RECOGNIZED"
        device_ok = "MEETS_DEVICE_INTEGRITY" in device_verdicts

        if not (app_ok and device_ok):
            # logger.warning(
            #     "Play Integrity: verification FAILED — app_ok=%s device_ok=%s",
            #     app_ok,
            #     device_ok,
            # )
            return JsonResponse(
                {
                    "error": "Device integrity verification failed.",
                    "app_recognition_verdict": app_verdict,
                    "device_recognition_verdict": device_verdicts,
                },
                status=403,
            )

        # ── 6. Issue a signed device JWT (valid 3 days) ──────────────────
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
            # logger.error("Play Integrity: JWT signing failed — %s", exc)
            return JsonResponse({"error": "Token generation error."}, status=500)

        # logger.info(
        #     "Play Integrity: issued device_token for pkg=%s expires=%s",
        #     settings.ANDROID_PACKAGE_NAME,
        #     (now + timedelta(days=3)).isoformat(),
        # )

        return JsonResponse({"device_token": device_token})
