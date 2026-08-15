"""Shared fixtures for calendar_events app tests."""

import pytest
from django.utils import timezone

from apps.calendar_events.models import Event
from apps.tasks.models import Task


@pytest.fixture
def event(user) -> Event:
    start = timezone.now().replace(microsecond=0)
    return Event.objects.create(
        user=user,
        title='Dentist appointment',
        start_time=start,
        end_time=start + timezone.timedelta(hours=1),
    )


@pytest.fixture
def task_for_event(user) -> Task:
    return Task.objects.create(user=user, title='Prepare quarterly report')
