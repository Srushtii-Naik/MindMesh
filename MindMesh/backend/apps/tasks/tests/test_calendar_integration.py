"""Tests for the tasks/services.py entry point used by apps.calendar_events
(ROADMAP.md Milestone 5 cross-domain integration)."""

import datetime as dt

import pytest

from apps.tasks.models import Task
from apps.tasks.services import get_tasks_due_between

pytestmark = pytest.mark.django_db


def test_get_tasks_due_between_returns_only_tasks_in_range(user):
    today = dt.date.today()
    Task.objects.create(user=user, title='Due today', due_date=today)
    Task.objects.create(user=user, title='Due tomorrow', due_date=today + dt.timedelta(days=1))
    Task.objects.create(user=user, title='Due next month', due_date=today + dt.timedelta(days=30))
    Task.objects.create(user=user, title='No due date')

    results = get_tasks_due_between(user, today, today + dt.timedelta(days=1))

    titles = {task.title for task in results}
    assert titles == {'Due today', 'Due tomorrow'}


def test_get_tasks_due_between_scoped_to_user(user, other_user):
    today = dt.date.today()
    Task.objects.create(user=user, title='Mine', due_date=today)
    Task.objects.create(user=other_user, title='Not mine', due_date=today)

    results = get_tasks_due_between(user, today, today)

    titles = [task.title for task in results]
    assert titles == ['Mine']
