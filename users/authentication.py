"""
Custom authentication that enforces single-session (anti-sharing).

How it works:
  1. Standard TokenAuthentication validates the DRF auth token.
  2. Then we compare the session_id sent in the request header (X-Session-Id)
     with the session_id stored on the User record.
  3. If they don't match → 401 Unauthorized (the user logged in on another device).

Header format:
    Authorization: Token <token>
    X-Session-Id: <session_id>

Backward compatibility:
  - If the user has NO session_id in the database yet (old users who haven't
    logged in since this feature went live), we allow the request through and
    skip the session check.  The next login will set their session_id.
  - If the client does NOT send the X-Session-Id header, standard auth still
    works (graceful rollout).  Once the mobile app starts sending the header,
    enforcement kicks in automatically.
"""

from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
import logging

logger = logging.getLogger('users')


class SessionAwareTokenAuthentication(TokenAuthentication):
    """
    Extends DRF's TokenAuthentication with single-session enforcement.
    """

    def authenticate(self, request):
        # First, run normal token auth
        result = super().authenticate(request)
        if result is None:
            return None  # no token provided → let other auth backends try

        user, token = result

        # Read the session id from the request header
        client_session_id = request.META.get('HTTP_X_SESSION_ID', '').strip()

        # Only enforce if BOTH the server and client have a session_id
        if user.session_id and client_session_id:
            if client_session_id != user.session_id:
                logger.warning(
                    f"🚫 Session mismatch for {user.email}: "
                    f"client={client_session_id[:8]}… vs db={user.session_id[:8]}…"
                )
                raise AuthenticationFailed(
                    detail={
                        'detail': 'Your session has been invalidated because you logged in on another device. '
                                  'Please log in again.',
                        'code': 'session_invalidated',
                    },
                )

        return (user, token)
