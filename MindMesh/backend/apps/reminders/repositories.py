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
    """Reminders due at or before `before` that haven't fired yet, scoped to
    a single user."""
    return list_reminders_for_user(user).filter(is_sent=False, remind_at__lte=before)


def list_all_due_reminders(before: datetime) -> QuerySet[Reminder]:
    """
    System-wide due, unsent reminders — deliberately *not* scoped to a
    single user, unlike every other query in this module.

    Consumed exclusively by the Milestone 9 notification engine's Celery
    Beat scan (apps.notifications.tasks.scan_due_reminders_task), which
    processes all users' reminders in one periodic pass rather than being
    triggered by a per-user request. Row-level ownership (PROJECT_RULES.md
    Section 7) is preserved downstream: each reminder still carries its own
    `user`, and apps.notifications.services processes it in that user's
    context — this function only removes the *query-time* filter, not the
    ownership relationship itself.
    """
    return Reminder.objects.select_related('user').filter(
        is_active=True, is_sent=False, remind_at__lte=before
    )
