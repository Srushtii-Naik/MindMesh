"""
Test settings.

Used exclusively by the automated test suite (see pytest.ini). Overrides
whatever is in the environment with deterministic, self-contained values so
tests never depend on a developer's local `.env`, a running Postgres
instance, a running Redis instance, or real Google/email credentials —
per PROJECT_RULES.md Section 12 ("Test before merging").
"""

from .base import *  # noqa: F401,F403

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# DRF's ScopedRateThrottle (config/settings/base.py) reads/writes through the
# default cache. Overridden here to an in-process cache for the same reason
# DATABASES/EMAIL_BACKEND are overridden above — tests must not depend on a
# running Redis instance.
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Tasks run synchronously, in-process — no broker required for tests.
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# A fixed, valid-looking client ID so GoogleLoginView's "is OAuth configured"
# check passes; the actual verification call is mocked in tests that exercise it.
GOOGLE_OAUTH_CLIENT_ID = 'test-client-id.apps.googleusercontent.com'

FRONTEND_URL = 'http://localhost:5173'

PASSWORD_HASHERS = [
    # Fast hasher for tests only — never used outside the test settings module.
    'django.contrib.auth.hashers.MD5PasswordHasher',
]
