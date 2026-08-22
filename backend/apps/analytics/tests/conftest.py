"""Shared fixtures for analytics app tests."""

from datetime import timedelta

import pytest
from django.utils import timezone

from apps.tasks.models import Task


def _backdate(task: Task, *, created_at=None, completed_at=None) -> Task:
    """Task.created_at uses auto_now_add, so it can't be set via .create();
    bulk .update() bypasses that (same trick used in apps.family.services
    for FamilyInvitation housekeeping)."""
    fields = {}
    if created_at is not None:
        fields['created_at'] = created_at
    if completed_at is not None:
        fields['completed_at'] = completed_at
    Task.objects.filter(id=task.id).update(**fields)
    task.refresh_from_db()
    return task


@pytest.fixture
def completed_task_factory(user):
    """Creates a completed task whose created_at/completed_at fall on a
    given date, for productivity/habit-streak tests."""

    def _make(*, on_date, title='Completed task'):
        moment = timezone.make_aware(
            timezone.datetime.combine(on_date, timezone.datetime.min.time())
        ) + timedelta(hours=9)
        task = Task.objects.create(user=user, title=title, is_completed=True)
        return _backdate(task, created_at=moment, completed_at=moment)

    return _make


@pytest.fixture
def created_task_factory(user):
    """Creates an (incomplete) task whose created_at falls on a given date."""

    def _make(*, on_date, title='Created task'):
        moment = timezone.make_aware(
            timezone.datetime.combine(on_date, timezone.datetime.min.time())
        ) + timedelta(hours=9)
        task = Task.objects.create(user=user, title=title)
        return _backdate(task, created_at=moment)

    return _make
