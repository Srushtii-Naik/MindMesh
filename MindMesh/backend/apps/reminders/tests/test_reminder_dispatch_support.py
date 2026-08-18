"""
Tests for the reminders service/repository functions added in Milestone 9
to support the notification engine's periodic scan: get_due_reminders and
mark_reminder_sent (apps.reminders.services). The scan itself is tested
end-to-end in apps/notifications/tests/test_reminder_engine.py.
"""

import pytest
from django.utils import timezone

from apps.reminders.models import Reminder
from apps.reminders.services import get_due_reminders, mark_reminder_sent

pytestmark = pytest.mark.django_db


def test_get_due_reminders_returns_only_past_due_unsent_reminders(user, other_user):
    due = Reminder.objects.create(
        user=user, title='Due', remind_at=timezone.now() - timezone.timedelta(minutes=1)
    )
    Reminder.objects.create(
        user=user, title='Future', remind_at=timezone.now() + timezone.timedelta(hours=1)
    )
    already_sent = Reminder.objects.create(
        user=user,
        title='Already sent',
        remind_at=timezone.now() - timezone.timedelta(minutes=5),
        is_sent=True,
    )
    # Due, but belongs to a different user — confirms the system-wide query
    # still returns it (no user filter), since ownership is preserved via
    # the FK, not by scoping this particular query.
    other_due = Reminder.objects.create(
        user=other_user, title="Other user's due", remind_at=timezone.now() - timezone.timedelta(minutes=1)
    )

    results = get_due_reminders()

    ids = {r.id for r in results}
    assert due.id in ids
    assert other_due.id in ids
    assert already_sent.id not in ids
    assert all(r.remind_at <= timezone.now() for r in results)


def test_get_due_reminders_excludes_inactive_reminders(user):
    from apps.reminders.services import delete_reminder_for_user

    reminder = Reminder.objects.create(
        user=user, title='Soft deleted', remind_at=timezone.now() - timezone.timedelta(minutes=1)
    )
    delete_reminder_for_user(user, reminder.id)

    results = get_due_reminders()

    assert reminder.id not in {r.id for r in results}


def test_mark_reminder_sent_sets_flag_and_timestamp(user):
    reminder = Reminder.objects.create(
        user=user, title='Due', remind_at=timezone.now() - timezone.timedelta(minutes=1)
    )

    updated = mark_reminder_sent(reminder)

    assert updated.is_sent is True
    assert updated.sent_at is not None
