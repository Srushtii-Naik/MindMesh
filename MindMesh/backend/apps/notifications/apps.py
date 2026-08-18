from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    """
    notifications domain app.

    Implements ROADMAP.md Milestone 9 — Notifications: the reminder
    delivery engine, email/push channels, and the in-app notification
    center, per ARCHITECTURE.md Section 3 & 9 module boundaries.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.notifications'
