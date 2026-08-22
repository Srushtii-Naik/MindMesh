"""Tests for apps.notifications.tasks — thin Celery wrappers around the
services already covered in test_services.py/test_reminder_engine.py.
CELERY_TASK_ALWAYS_EAGER=True (config/settings/test.py) makes these run
synchronously in-process."""

import pytest
from django.core import mail

from apps.notifications.models import DeliveryStatus, NotificationChannel
from apps.notifications.services import create_notification_for_user
from apps.notifications.tasks import (
    deliver_notification_email_task,
    deliver_notification_push_task,
    scan_due_reminders_task,
)

pytestmark = pytest.mark.django_db


def test_scan_due_reminders_task_returns_processed_count(due_reminder, future_reminder):
    processed = scan_due_reminders_task()

    assert processed == 1
    due_reminder.refresh_from_db()
    assert due_reminder.is_sent is True


def test_deliver_notification_email_task_sends_and_marks_sent(user):
    notification = create_notification_for_user(
        user, notification_type='system', title='Task email', channels=[]
    )
    delivery = notification.deliveries.create(channel=NotificationChannel.EMAIL)

    deliver_notification_email_task(delivery_id=str(delivery.id))

    delivery.refresh_from_db()
    assert delivery.status == DeliveryStatus.SENT
    assert len(mail.outbox) == 1


def test_deliver_notification_email_task_noop_for_missing_delivery():
    # Should not raise even though this delivery doesn't exist.
    deliver_notification_email_task(delivery_id='00000000-0000-0000-0000-000000000000')


def test_deliver_notification_push_task_uses_console_sender(user):
    from apps.notifications.services import register_device_token_for_user

    register_device_token_for_user(user, token='device-1')
    notification = create_notification_for_user(
        user, notification_type='system', title='Task push', channels=[]
    )
    delivery = notification.deliveries.create(channel=NotificationChannel.PUSH)

    deliver_notification_push_task(delivery_id=str(delivery.id))

    delivery.refresh_from_db()
    assert delivery.status == DeliveryStatus.SENT


def test_deliver_notification_push_task_noop_for_missing_delivery():
    deliver_notification_push_task(delivery_id='00000000-0000-0000-0000-000000000000')
