"""
Root URL configuration.

Per ARCHITECTURE.md Section 3 & 6: all endpoints are namespaced under /api/v1/
to allow non-breaking evolution. Domain routes (tasks, notes, calendar, AI, etc.)
are included here as they're built in later milestones.
"""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('common.urls')),
    path('api/v1/auth/', include('apps.accounts.urls')),
    path('api/v1/tasks/', include('apps.tasks.urls')),
    path('api/v1/calendar/', include('apps.calendar_events.urls')),
    path('api/v1/reminders/', include('apps.reminders.urls')),
    path('api/v1/notes/', include('apps.notes.urls')),
    path('api/v1/ai/', include('apps.ai_companion.urls')),
    path('api/v1/notifications/', include('apps.notifications.urls')),
    path('api/v1/family/', include('apps.family.urls')),
    path('api/v1/analytics/', include('apps.analytics.urls')),
    # Further domain routes are added starting in later milestones.
]

# --------------------------------------------------------------------------
# Milestone 12 — optional built-in static-file serving.
#
# DEBUG=True (development/test) already gets static files from Django's
# runserver automatically; this covers the opposite case — DEBUG=False
# deployments (production.py) that don't have an Nginx/CDN in front of
# Django to serve /static/ (e.g. the admin's CSS/JS on Railway, which has
# no Nginx sidecar). Self-hosted deployments using
# infra/nginx/nginx.prod.conf serve /static/ via Nginx directly instead and
# should leave DJANGO_SERVE_STATIC unset/False — see that config's
# `location /static/` block.
#
# This intentionally doesn't add whitenoise (PROJECT_RULES.md Section 2 —
# "No new dependencies. Reuse what exists"); it's a functional fallback,
# not a high-throughput static file server. The admin panel is a low-traffic
# internal tool, not the product's primary surface, so this tradeoff is
# acceptable rather than requiring a locked-stack revision.
# --------------------------------------------------------------------------
if not settings.DEBUG and getattr(settings, 'DJANGO_SERVE_STATIC', False):
    from django.views.static import serve as serve_static

    urlpatterns += [
        path(
            'static/<path:path>',
            serve_static,
            {'document_root': settings.STATIC_ROOT},
        ),
    ]
