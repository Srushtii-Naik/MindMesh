"""
Production settings.

Hardened per ARCHITECTURE.md Section 10 (Security Strategy). Full production
hardening (e.g., HSTS, secure cookies audit, monitoring hooks) is completed in
Milestone 12 — Production & Deployment. This file establishes safe defaults
now so production is never accidentally run with development settings.
"""

from .base import *  # noqa: F401,F403
from .base import env

DEBUG = False

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=[])
