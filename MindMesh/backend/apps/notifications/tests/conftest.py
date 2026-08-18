"""Shared fixtures for notifications app tests."""

import pytest
from django.utils import timezone

from apps.notifications.models import NotificationChannel
from apps.notifications.services import create_notification_for_user
from apps.reminders.models import Reminder


@pytest.fixture
def notification(user):
    return create_notification_for_user(
        user,
        notification_type='system',
        title='Welcome to MindMesh',
        message='Thanks for joining.',
        channels=[NotificationChannel.IN_APP],
    )


@pytest.fixture
def due_reminder(user) -> Reminder:
    """A reminder whose remind_at is already in the past — i.e. due now."""
    return Reminder.objects.create(
        user=user,
        title='Take medication',
        message='Take your evening medication.',
        remind_at=timezone.now() - timezone.timedelta(minutes=1),
    )


@pytest.fixture
def future_reminder(user) -> Reminder:
    """A reminder that is not yet due."""
    return Reminder.objects.create(
        user=user,
        title='Team standup',
        message='Daily standup meeting.',
        remind_at=timezone.now() + timezone.timedelta(hours=2),
    )
