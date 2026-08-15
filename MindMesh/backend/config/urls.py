"""
Root URL configuration.

Per ARCHITECTURE.md Section 3 & 6: all endpoints are namespaced under /api/v1/
to allow non-breaking evolution. Domain routes (tasks, notes, calendar, AI, etc.)
are included here as they're built in later milestones.
"""

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
    # Further domain routes are added starting in later milestones.
]
