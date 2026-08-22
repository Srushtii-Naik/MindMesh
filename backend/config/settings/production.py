"""
Production settings.

Hardened per ARCHITECTURE.md Section 10 (Security Strategy) and
PROJECT_RULES.md Section 8. This is the full Milestone 12 hardening pass —
every setting here is either a stricter override of base.py or a required
value that must be supplied via environment variables in the deployed
environment (Railway). Nothing in this file silently falls back to an
insecure default.
"""

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F401,F403
from .base import env

DEBUG = False

# --------------------------------------------------------------------------
# Fail loudly rather than deploy with an insecure default. A missing/short
# SECRET_KEY or an empty ALLOWED_HOSTS list is exactly the kind of "shortcut
# justified by it's just for now" PROJECT_RULES.md Section 1 forbids.
# --------------------------------------------------------------------------

if SECRET_KEY in ('', 'insecure-development-key-change-me') or len(SECRET_KEY) < 32:
    raise ImproperlyConfigured(
        'DJANGO_SECRET_KEY must be set to a strong, unique value in production. '
        'Generate one with: python -c "import secrets; print(secrets.token_urlsafe(50))"'
    )

ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=[])
if not ALLOWED_HOSTS:
    raise ImproperlyConfigured('DJANGO_ALLOWED_HOSTS must be set in production.')

if not CSRF_TRUSTED_ORIGINS:
    raise ImproperlyConfigured(
        'CSRF_TRUSTED_ORIGINS must be set in production (e.g. '
        'https://api.mindmesh.app) — required for the Django admin\'s '
        'session-based CSRF protection.'
    )

# --------------------------------------------------------------------------
# Transport security
# --------------------------------------------------------------------------

SECURE_SSL_REDIRECT = env.bool('DJANGO_SECURE_SSL_REDIRECT', default=True)
# Railway terminates TLS at its edge proxy and forwards plain HTTP internally,
# so Django must trust the X-Forwarded-Proto header to correctly detect HTTPS
# (otherwise SECURE_SSL_REDIRECT loops forever, and request.is_secure() is
# always False, breaking secure-cookie logic and SIMPLE_JWT's expectations).
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SECURE_HSTS_SECONDS = env.int('DJANGO_SECURE_HSTS_SECONDS', default=31536000)  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# --------------------------------------------------------------------------
# Cookies
# --------------------------------------------------------------------------

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True

# Refresh-token cookie (apps/accounts/cookies.py) — Secure is forced
# regardless of AUTH_COOKIE_SECURE's env value, since production must always
# be HTTPS-only. SameSite defaults to 'None' since the Vercel frontend and
# Railway backend are different origins; 'None' requires Secure=True, which
# is guaranteed above.
AUTH_COOKIE_SECURE = True
AUTH_COOKIE_SAMESITE = env('AUTH_COOKIE_SAMESITE', default='None')

# --------------------------------------------------------------------------
# Static files — see config/urls.py's DJANGO_SERVE_STATIC block for why this
# exists and when to use it vs. an Nginx/CDN front.
# --------------------------------------------------------------------------

DJANGO_SERVE_STATIC = env.bool('DJANGO_SERVE_STATIC', default=False)
