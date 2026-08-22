"""
Domain models — Calendar & Scheduling.

Per ARCHITECTURE.md Section 4: every domain table is scoped to a user_id
with row-level ownership enforced at the service layer, and timestamps are
standardized across all tables. Event is user-generated content, so it uses
soft deletes per PROJECT_RULES.md Section 7.

`task` is a nullable link to apps.tasks.Task, matching ARCHITECTURE.md
Section 4's description of the Calendar/Events entity group ("associations
to tasks/reminders"). This is a persistence-layer relationship declared on
the model, not a service-layer reach-in — cross-domain *business logic*
(e.g. resolving/validating a task_id on write) goes through
apps.tasks.services, never through this FK directly (see services.py).
"""

import uuid

from django.conf import settings
from django.db import models


class Event(models.Model):
    """A single calendar event owned by a user, optionally linked to a task."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='events'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    location = models.CharField(max_length=255, blank=True, default='')

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    all_day = models.BooleanField(default=False)
    color = models.CharField(max_length=7, default='#5f6dfa')  # brand-500

    task = models.ForeignKey(
        'tasks.Task',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='calendar_events',
    )

    # Soft delete (PROJECT_RULES.md Section 7).
    is_active = models.BooleanField(default=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'calendar_events_event'
        ordering = ['start_time']
        verbose_name = 'event'
        verbose_name_plural = 'events'
        indexes = [
            models.Index(fields=['user', 'is_active', 'start_time']),
            models.Index(fields=['user', 'is_active', 'end_time']),
        ]

    def __str__(self) -> str:
        return self.title
