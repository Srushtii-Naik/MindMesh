"""
URL routes — Reminders.

Mounted at /api/v1/reminders/ from config/urls.py, per ARCHITECTURE.md
Section 6 API versioning convention.
"""

from django.urls import path

from apps.reminders.views import ReminderDetailView, ReminderListCreateView

urlpatterns = [
    path('', ReminderListCreateView.as_view(), name='reminder-list'),
    path('<uuid:reminder_id>/', ReminderDetailView.as_view(), name='reminder-detail'),
]
