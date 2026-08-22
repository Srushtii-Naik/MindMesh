"""
Refresh-token cookie & CSRF helpers.

Implements the migration flagged by ADR 0001
(docs/adr/0001-token-storage-strategy.md) and required by PROJECT_RULES.md
Section 8 / ROADMAP.md Milestone 12's security audit: the JWT refresh token
is delivered as an httpOnly cookie rather than in the JSON response body,
removing it from JavaScript's reach and therefore from XSS exfiltration
(ADR 0001, "Security Trade-off").

Because the browser now attaches the refresh cookie to requests
automatically, the endpoints that read it (token refresh, logout) are
protected with a "double submit cookie" CSRF check: a second, non-httpOnly
cookie holds a random token that only same-origin JavaScript can read back
and echo as a request header. A cross-site attacker can trigger the request
(the cookie still gets sent) but cannot read the CSRF cookie's value to
supply a matching header, so the check fails. This is deliberately a
self-contained comparison rather than Django's own CSRF machinery — DRF's
APIView unconditionally marks every view csrf_exempt (so
CsrfViewMiddleware never runs for API endpoints; see ADR 0001's "What Would
Need to Change" section), and Django's CSRF token masking internals are not
public API to build against.
"""

import secrets

from django.conf import settings
from rest_framework.request import Request
from rest_framework.response import Response

# Scoped to /api/v1/auth/ only — the refresh/CSRF cookies are meaningless
# (and shouldn't be sent) outside the auth endpoints that read them.
REFRESH_COOKIE_PATH = '/api/v1/auth/'

CSRF_HEADER_NAME = 'HTTP_X_CSRF_TOKEN'


def _refresh_cookie_max_age() -> int:
    return int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds())


def attach_refresh_cookie(response: Response, refresh_token: str) -> str:
    """
    Set the httpOnly refresh-token cookie and a fresh, JS-readable CSRF
    cookie on `response`. Called on register/login/google-login (new
    session) and token refresh (rotated session). Returns the new CSRF
    token value (mainly useful for tests).
    """
    max_age = _refresh_cookie_max_age()

    response.set_cookie(
        settings.AUTH_REFRESH_COOKIE_NAME,
        refresh_token,
        max_age=max_age,
        httponly=True,
        secure=settings.AUTH_COOKIE_SECURE,
        samesite=settings.AUTH_COOKIE_SAMESITE,
        domain=settings.AUTH_COOKIE_DOMAIN,
        path=REFRESH_COOKIE_PATH,
    )

    csrf_token = secrets.token_urlsafe(32)
    response.set_cookie(
        settings.AUTH_CSRF_COOKIE_NAME,
        csrf_token,
        max_age=max_age,
        httponly=False,  # must be readable by frontend JS to echo as a header
        secure=settings.AUTH_COOKIE_SECURE,
        samesite=settings.AUTH_COOKIE_SAMESITE,
        domain=settings.AUTH_COOKIE_DOMAIN,
        path=REFRESH_COOKIE_PATH,
    )
    return csrf_token


def clear_refresh_cookie(response: Response) -> None:
    """Clear both auth cookies on logout."""
    response.delete_cookie(
        settings.AUTH_REFRESH_COOKIE_NAME,
        path=REFRESH_COOKIE_PATH,
        domain=settings.AUTH_COOKIE_DOMAIN,
        samesite=settings.AUTH_COOKIE_SAMESITE,
    )
    response.delete_cookie(
        settings.AUTH_CSRF_COOKIE_NAME,
        path=REFRESH_COOKIE_PATH,
        domain=settings.AUTH_COOKIE_DOMAIN,
        samesite=settings.AUTH_COOKIE_SAMESITE,
    )


def get_refresh_cookie(request: Request) -> str | None:
    return request.COOKIES.get(settings.AUTH_REFRESH_COOKIE_NAME)


def verify_csrf(request: Request) -> bool:
    """
    Double-submit CSRF check: the value in the (JS-readable) CSRF cookie
    must match the value the client echoed back in the X-CSRF-Token header.
    A cross-site attacker's browser will send the cookie automatically but
    cannot read its value to forge a matching header.
    """
    cookie_value = request.COOKIES.get(settings.AUTH_CSRF_COOKIE_NAME)
    header_value = request.META.get(CSRF_HEADER_NAME)
    if not cookie_value or not header_value:
        return False
    return secrets.compare_digest(cookie_value, header_value)
