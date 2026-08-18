"""
Service layer — Reminders.

Domain business logic for reminder CRUD. Per ARCHITECTURE.md Section 3:
views call services; services never import DRF.

Per ROADMAP.md Milestone 5, this milestone delivers the reminder *data
model and CRUD* only — actual delivery (push/email/in-app) is built in
Milestone 9. `is_sent` stays False for every reminder created here.

Task/event associations are resolved through apps.tasks.services and
apps.calendar_events.services (service interfaces), never by importing
those apps' models directly, per ARCHITECTURE.md Section 3.
"""

from datetime import datetime

from django.utils import timezone

from apps.accounts.models import User
from apps.calendar_events.services import EventNotFoundError, get_event
from apps.reminders.models import Reminder
from apps.reminders.repositories import (
    create_reminder,
    get_reminder_for_user,
    list_all_due_reminders,
    list_reminders_for_user,
    soft_delete_reminder,
    update_reminder,
)
from apps.tasks.services import TaskNotFoundError
from apps.tasks.services import get_task as get_task_for_user


class ReminderNotFoundError(Exception):
    """Raised when a reminder cannot be found for the requesting user."""


class LinkedTaskNotFoundError(Exception):
    """Raised when a reminder is linked to a task the user doesn't own."""


class LinkedEventNotFoundError(Exception):
    """Raised when a reminder is linked to an event the user doesn't own."""


def _resolve_task(user: User, task_id):
    if task_id is None:
        return None
    try:
        return get_task_for_user(user, task_id)
    except TaskNotFoundError as exc:
        raise LinkedTaskNotFoundError(str(exc)) from exc


def _resolve_event(user: User, event_id):
    if event_id is None:
        return None
    try:
        return get_event(user, event_id)
    except EventNotFoundError as exc:
        raise LinkedEventNotFoundError(str(exc)) from exc


def get_reminder(user: User, reminder_id) -> Reminder:
    reminder = get_reminder_for_user(user, reminder_id)
    if reminder is None:
        raise ReminderNotFoundError('Reminder not found.')
    return reminder


def list_reminders_for_user_filtered(
    user: User,
    *,
    is_sent: bool | None = None,
    before: datetime | None = None,
    after: datetime | None = None,
    task_id=None,
    event_id=None,
):
    queryset = list_reminders_for_user(user)

    if is_sent is not None:
        queryset = queryset.filter(is_sent=is_sent)
    if before is not None:
        queryset = queryset.filter(remind_at__lte=before)
    if after is not None:
        queryset = queryset.filter(remind_at__gte=after)
    if task_id:
        queryset = queryset.filter(task_id=task_id)
    if event_id:
        queryset = queryset.filter(event_id=event_id)

    return queryset


def create_reminder_for_user(
    user: User,
    *,
    title: str,
    remind_at: datetime,
    message: str = '',
    task_id=None,
    event_id=None,
) -> Reminder:
    task = _resolve_task(user, task_id)
    event = _resolve_event(user, event_id)

    return create_reminder(
        user=user,
        title=title.strip(),
        message=message,
        remind_at=remind_at,
        task=task,
        event=event,
    )


def update_reminder_for_user(user: User, reminder_id, **fields) -> Reminder:
    reminder = get_reminder_for_user(user, reminder_id)
    if reminder is None:
        raise ReminderNotFoundError('Reminder not found.')

    if 'task_id' in fields:
        fields['task'] = _resolve_task(user, fields.pop('task_id'))
    if 'event_id' in fields:
        fields['event'] = _resolve_event(user, fields.pop('event_id'))
    if 'title' in fields:
        fields['title'] = fields['title'].strip()

    return update_reminder(reminder, **fields)


def delete_reminder_for_user(user: User, reminder_id) -> None:
    reminder = get_reminder_for_user(user, reminder_id)
    if reminder is None:
        raise ReminderNotFoundError('Reminder not found.')
    soft_delete_reminder(reminder)


def get_due_reminders(before: datetime | None = None) -> list[Reminder]:
    """
    Reminders across *all* users that are due for delivery, for the
    Milestone 9 notification engine's periodic scan
    (apps.notifications.services.dispatch_due_reminder_notifications).

    Exposed as a service-layer function — never a direct repository/model
    import from apps.notifications — per ARCHITECTURE.md Section 3's
    cross-domain rule. Every other function in this module is user-scoped;
    this one intentionally isn't, since it backs a system-wide scheduled
    scan rather than a per-request call.
    """
    return list(list_all_due_reminders(before or timezone.now()))


def mark_reminder_sent(reminder: Reminder) -> Reminder:
    """Marks a reminder as delivered. Called by the notification engine once
    it has recorded the corresponding Notification for the reminder's user."""
    return update_reminder(reminder, is_sent=True, sent_at=timezone.now())
