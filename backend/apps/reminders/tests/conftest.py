"""Shared fixtures for reminders app tests."""

import pytest
from django.utils import timezone

from apps.reminders.models import Reminder


@pytest.fixture
def reminder(user) -> Reminder:
    return Reminder.objects.create(
        user=user, title='Take medication', remind_at=timezone.now() + timezone.timedelta(hours=2)
    )
