"""
Base Django settings for MindMesh.

Per ARCHITECTURE.md Section 3 & Section 10:
- Configuration is environment-variable driven; no secrets committed to source control.
- Settings are split per environment (base / development / production).

This module contains only foundation-stage configuration (Milestone 1).
Auth (JWT/OAuth), AI provider keys, and domain app settings are added in
their respective milestones per ROADMAP.md.
"""

from pathlib import Path
from datetime import timedelta

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DEBUG=(bool, False),
)

# Reads backend/.env if present (see .env.example for the documented template).
environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY = env('DJANGO_SECRET_KEY', default='insecure-development-key-change-me')
DEBUG = env.bool('DJANGO_DEBUG', default=False)
ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

# --------------------------------------------------------------------------
# Applications
# --------------------------------------------------------------------------

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
]

# Domain apps per ARCHITECTURE.md Section 3 & 9.
# Registered as empty scaffolds at this stage — no models/business logic yet.
LOCAL_APPS = [
    'common',
    'apps.accounts',
    'apps.tasks',
    'apps.notes',
    'apps.reminders',
    'apps.calendar_events',
    'apps.ai_companion',
    'apps.notifications',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# --------------------------------------------------------------------------
# Database — PostgreSQL is the system of record (ARCHITECTURE.md Section 4)
# --------------------------------------------------------------------------

DATABASES = {
    'default': env.db(
        'DATABASE_URL',
        default='postgres://mindmesh:mindmesh@localhost:5432/mindmesh',
    )
}

# --------------------------------------------------------------------------
# Redis — cache layer & Celery broker (ARCHITECTURE.md Section 8)
# --------------------------------------------------------------------------

REDIS_URL = env('REDIS_URL', default='redis://localhost:6379/0')

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': REDIS_URL,
    }
}

# --------------------------------------------------------------------------
# Celery (broker configured; task modules added per-domain from Milestone 5+)
# --------------------------------------------------------------------------

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
# Enables tests (and only tests) to run tasks synchronously, in-process,
# without a running broker. Never enabled outside of the test environment.
CELERY_TASK_ALWAYS_EAGER = env.bool('CELERY_TASK_ALWAYS_EAGER', default=False)

# --------------------------------------------------------------------------
# Custom user model (ARCHITECTURE.md Section 5 — email-based authentication)
# --------------------------------------------------------------------------

AUTH_USER_MODEL = 'accounts.User'

# --------------------------------------------------------------------------
# Password validation
# --------------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --------------------------------------------------------------------------
# Internationalization
# --------------------------------------------------------------------------

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# --------------------------------------------------------------------------
# Static files
# --------------------------------------------------------------------------

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --------------------------------------------------------------------------
# Django REST Framework — API layer conventions (ARCHITECTURE.md Section 6)
# --------------------------------------------------------------------------

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    # Secure-by-default per PROJECT_RULES.md Section 8: endpoints are private
    # unless explicitly marked AllowAny (e.g. register/login/health-check).
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    # Rate limiting (PROJECT_RULES.md Section 8 — "Rate limiting on auth and
    # AI-chat endpoints at minimum"). ScopedRateThrottle only throttles views
    # that declare a `throttle_scope`, so this has no effect on endpoints
    # that don't opt in (see apps/accounts/views.py for which ones do).
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.ScopedRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'auth_register': '5/min',
        'auth_login': '10/min',
        'auth_google': '10/min',
        'auth_token_refresh': '30/min',
        'auth_password_reset': '5/min',
        'auth_password_reset_confirm': '5/min',
        # AI-chat/summary endpoints (PROJECT_RULES.md Section 8 — "Rate
        # limiting on auth and AI-chat endpoints at minimum") — protects
        # against runaway AI provider cost, not just abuse.
        'notes_ai_summary': '20/min',
        'ai_chat': '20/min',
    },
}

# --------------------------------------------------------------------------
# JWT configuration (ARCHITECTURE.md Section 5 — Authentication Flow)
# --------------------------------------------------------------------------

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# --------------------------------------------------------------------------
# CORS — strict allow-list per ARCHITECTURE.md Section 10
# --------------------------------------------------------------------------

CORS_ALLOWED_ORIGINS = env.list(
    'CORS_ALLOWED_ORIGINS', default=['http://localhost:5173']
)

# --------------------------------------------------------------------------
# Google OAuth (ARCHITECTURE.md Section 5 — Google OAuth flow)
# --------------------------------------------------------------------------

GOOGLE_OAUTH_CLIENT_ID = env('GOOGLE_OAUTH_CLIENT_ID', default='')

# --------------------------------------------------------------------------
# Frontend URL — used to build links that leave the backend (e.g. the
# password reset link embedded in the reset email).
# --------------------------------------------------------------------------

FRONTEND_URL = env('FRONTEND_URL', default='http://localhost:5173')

# --------------------------------------------------------------------------
# Email (password reset notifications)
# --------------------------------------------------------------------------
#
# Defaults to Django's console backend so reset emails are visible in
# server logs during development without requiring real SMTP credentials.
# A real backend (SMTP/SES/etc.) is configured via EMAIL_BACKEND in
# staging/production environments.

EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='MindMesh <no-reply@mindmesh.app>')

# --------------------------------------------------------------------------
# Media files — user uploads (ROADMAP.md Milestone 6: Notes attachments).
# Not served under a public MEDIA_URL route; apps.notes serves attachments
# exclusively through its own authenticated, ownership-checked download
# endpoint (see apps/notes/views.py), so no urls.py wiring is needed here.
# --------------------------------------------------------------------------

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# --------------------------------------------------------------------------
# Notes attachments (ROADMAP.md Milestone 6 — "Attachments upload/storage
# implemented securely"). Kept here rather than hardcoded in apps/notes so
# limits are environment-configurable without a code change.
# --------------------------------------------------------------------------

NOTE_ATTACHMENT_MAX_SIZE_BYTES = env.int('NOTE_ATTACHMENT_MAX_SIZE_BYTES', default=10 * 1024 * 1024)
NOTE_ATTACHMENT_ALLOWED_CONTENT_TYPES = [
    'image/png',
    'image/jpeg',
    'image/gif',
    'image/webp',
    'application/pdf',
    'text/plain',
]

# --------------------------------------------------------------------------
# AI Provider Abstraction Layer (ARCHITECTURE.md Section 7). Brought forward
# minimally in Milestone 6 to power Notes' AI summaries; the full chat/
# memory surface is configured further in Milestones 7-8. Defaults to the
# offline `stub` provider so the app is fully usable without vendor API
# keys — set AI_PROVIDER to `gemini` or `openai` once keys are supplied.
# --------------------------------------------------------------------------

AI_PROVIDER = env('AI_PROVIDER', default='stub')
GEMINI_API_KEY = env('GEMINI_API_KEY', default='')
OPENAI_API_KEY = env('OPENAI_API_KEY', default='')
OPENAI_MODEL = env('OPENAI_MODEL', default='gpt-4o-mini')
AI_SUMMARY_TIMEOUT_SECONDS = env.int('AI_SUMMARY_TIMEOUT_SECONDS', default=15)
