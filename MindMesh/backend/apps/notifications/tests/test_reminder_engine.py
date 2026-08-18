"""
End-to-end tests for the Milestone 9 reminder-delivery engine:
apps.notifications.services.dispatch_due_reminder_notifications, which is
what apps.notifications.tasks.scan_due_reminders_task calls on its Celery
Beat schedule.
"""

import pytest
from django.core import mail

from apps.accounts.services import update_settings_for_user
from apps.notifications.models import (
    DeliveryStatus,
    Notification,
    NotificationChannel,
    NotificationType,
)
from apps.notifications.services import (
    dispatch_due_reminder_notifications,
    register_device_token_for_user,
)

pytestmark = pytest.mark.django_db


def test_dispatch_processes_due_reminder_and_marks_it_sent(user, due_reminder):
    processed = dispatch_due_reminder_notifications()

    assert processed == 1

    due_reminder.refresh_from_db()
    assert due_reminder.is_sent is True
    assert due_reminder.sent_at is not None

    notification = Notification.objects.get(user=user, reminder=due_reminder)
    assert notification.notification_type == NotificationType.REMINDER
    assert notification.title == due_reminder.title


def test_dispatch_ignores_future_reminders(future_reminder):
    processed = dispatch_due_reminder_notifications()

    assert processed == 0
    future_reminder.refresh_from_db()
    assert future_reminder.is_sent is False
    assert Notification.objects.count() == 0


def test_dispatch_creates_in_app_and_email_deliveries_by_default(user, due_reminder):
    dispatch_due_reminder_notifications()

    notification = Notification.objects.get(reminder=due_reminder)
    channels = set(notification.deliveries.values_list('channel', flat=True))

    assert NotificationChannel.IN_APP in channels
    assert NotificationChannel.EMAIL in channels
    assert NotificationChannel.PUSH not in channels  # no device token registered

    assert len(mail.outbox) == 1
    email_delivery = notification.deliveries.get(channel=NotificationChannel.EMAIL)
    assert email_delivery.status == DeliveryStatus.SENT


def test_dispatch_skips_email_when_user_disabled_it(user, due_reminder):
    update_settings_for_user(user, email_notifications_enabled=False)

    dispatch_due_reminder_notifications()

    notification = Notification.objects.get(reminder=due_reminder)
    channels = set(notification.deliveries.values_list('channel', flat=True))

    assert NotificationChannel.EMAIL not in channels
    assert len(mail.outbox) == 0


def test_dispatch_includes_push_channel_when_device_registered(user, due_reminder):
    register_device_token_for_user(user, token='device-token-1')

    dispatch_due_reminder_notifications()

    notification = Notification.objects.get(reminder=due_reminder)
    push_delivery = notification.deliveries.get(channel=NotificationChannel.PUSH)
    assert push_delivery.status == DeliveryStatus.SENT


def test_dispatch_processes_multiple_users_independently(user, other_user, due_reminder):
    from django.utils import timezone

    from apps.reminders.models import Reminder

    other_due = Reminder.objects.create(
        user=other_user,
        title="Other user's reminder",
        remind_at=timezone.now() - timezone.timedelta(minutes=5),
    )

    processed = dispatch_due_reminder_notifications()

    assert processed == 2
    assert Notification.objects.filter(user=user, reminder=due_reminder).exists()
    assert Notification.objects.filter(user=other_user, reminder=other_due).exists()


def test_dispatch_does_not_reprocess_already_sent_reminders(due_reminder):
    first_pass = dispatch_due_reminder_notifications()
    second_pass = dispatch_due_reminder_notifications()

    assert first_pass == 1
    assert second_pass == 0
    assert Notification.objects.count() == 1
