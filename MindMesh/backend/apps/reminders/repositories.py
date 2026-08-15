"""
Repository / data-access layer — Reminders.

Encapsulates ORM queries for Reminder, isolating persistence details from
the service layer, per ARCHITECTURE.md Section 3. Every query here is
scoped to a given user — row-level ownership per PROJECT_RULES.md Section 7.
"""

from datetime import datetime

from django.db.models import QuerySet
from django.utils import timezone

from apps.accounts.models import User
from apps.reminders.models import Reminder


def list_reminders_for_user(user: User) -> QuerySet[Reminder]:
    """Base queryset of the user's non-deleted reminders. Filters applied by the service layer."""
    return Reminder.objects.filter(user=user, is_active=True)


def get_reminder_for_user(user: User, reminder_id) -> Reminder | None:
    return Reminder.objects.filter(user=user, id=reminder_id, is_active=True).first()


def create_reminder(*, user: User, **fields) -> Reminder:
    return Reminder.objects.create(user=user, **fields)


def update_reminder(reminder: Reminder, **fields) -> Reminder:
    for field, value in fields.items():
        setattr(reminder, field, value)
    reminder.save()
    return reminder


def soft_delete_reminder(reminder: Reminder) -> None:
    reminder.is_active = False
    reminder.deleted_at = timezone.now()
    reminder.save(update_fields=['is_active', 'deleted_at', 'updated_at'])


def list_due_reminders(user: User, before: datetime) -> QuerySet[Reminder]:
    """Reminders due at or before `before` that haven't fired yet. Not yet consumed
    anywhere — reserved for the Milestone 9 delivery engine (Celery Beat scan)."""
    return list_reminders_for_user(user).filter(is_sent=False, remind_at__lte=before)
