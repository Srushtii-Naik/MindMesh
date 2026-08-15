"""
Domain models — Reminders.

Per ROADMAP.md Milestone 5, this milestone establishes reminders'
*foundational data model* only — the delivery mechanism (push/email/in-app,
scheduled Celery Beat firing) is built in Milestone 9 (Notifications). This
mirrors ARCHITECTURE.md Section 4's "Reminders — reminder schedules" entity
group and its Section 8 note that reminders/notifications are a later-stage
concern for the background-jobs layer.

`trigger_type` is deliberately kept extensible (PRD.md Section 7: "flexible
triggers (time-based, location-based, and context-based)") even though only
`time` is usable today — location/context triggers are explicitly out of
scope until a later milestone builds the supporting infrastructure.
"""

import uuid

from django.conf import settings
from django.db import models


class ReminderTriggerType(models.TextChoices):
    TIME = 'time', 'Time-based'


class Reminder(models.Model):
    """A user-owned reminder, optionally linked to a task and/or a calendar event."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reminders'
    )
    title = models.CharField(max_length=255)
    message = models.TextField(blank=True, default='')

    trigger_type = models.CharField(
        max_length=10, choices=ReminderTriggerType.choices, default=ReminderTriggerType.TIME
    )
    remind_at = models.DateTimeField()

    task = models.ForeignKey(
        'tasks.Task',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reminders',
    )
    event = models.ForeignKey(
        'calendar_events.Event',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reminders',
    )

    # Delivery status — set by the Milestone 9 notification engine. Always
    # False at this stage since nothing sends reminders yet.
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)

    # Soft delete (PROJECT_RULES.md Section 7).
    is_active = models.BooleanField(default=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reminders_reminder'
        ordering = ['remind_at']
        verbose_name = 'reminder'
        verbose_name_plural = 'reminders'
        indexes = [
            models.Index(fields=['user', 'is_active', 'remind_at']),
            models.Index(fields=['user', 'is_active', 'is_sent']),
        ]

    def __str__(self) -> str:
        return self.title
