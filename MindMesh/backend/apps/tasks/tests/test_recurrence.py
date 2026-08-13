from datetime import date

import pytest
from django.urls import reverse

from apps.tasks.models import RecurrenceRule, Task
from apps.tasks.services import _add_months, _advance_due_date, generate_next_occurrence

pytestmark = pytest.mark.django_db


class TestDateMath:
    def test_add_months_simple(self):
        assert _add_months(date(2026, 1, 15), 1) == date(2026, 2, 15)

    def test_add_months_across_year_boundary(self):
        assert _add_months(date(2026, 12, 15), 1) == date(2027, 1, 15)

    def test_add_months_clamps_to_shorter_month(self):
        # Jan 31 + 1 month -> Feb has only 28 days in 2026 (not a leap year)
        assert _add_months(date(2026, 1, 31), 1) == date(2026, 2, 28)

    def test_advance_due_date_daily(self):
        assert _advance_due_date(date(2026, 1, 1), RecurrenceRule.DAILY, 3) == date(2026, 1, 4)

    def test_advance_due_date_weekly(self):
        assert _advance_due_date(date(2026, 1, 1), RecurrenceRule.WEEKLY, 2) == date(2026, 1, 15)

    def test_advance_due_date_monthly(self):
        assert _advance_due_date(date(2026, 1, 1), RecurrenceRule.MONTHLY, 1) == date(2026, 2, 1)

    def test_advance_due_date_defaults_to_today_when_no_due_date(self):
        from django.utils import timezone

        result = _advance_due_date(None, RecurrenceRule.DAILY, 1)
        assert result == timezone.localdate() + __import__('datetime').timedelta(days=1)


class TestGenerateNextOccurrence:
    def test_non_recurring_task_generates_nothing(self, user):
        task = Task.objects.create(user=user, title='One-off', recurrence=RecurrenceRule.NONE)
        assert generate_next_occurrence(task) is None

    def test_daily_recurrence_generates_next_task(self, user):
        task = Task.objects.create(
            user=user,
            title='Daily standup notes',
            recurrence=RecurrenceRule.DAILY,
            recurrence_interval=1,
            due_date=date(2026, 3, 1),
        )

        next_task = generate_next_occurrence(task)

        assert next_task is not None
        assert next_task.id != task.id
        assert next_task.title == task.title
        assert next_task.due_date == date(2026, 3, 2)
        assert next_task.is_completed is False
        assert next_task.recurrence_parent_id == task.id

    def test_weekly_recurrence_with_interval(self, user):
        task = Task.objects.create(
            user=user,
            title='Biweekly review',
            recurrence=RecurrenceRule.WEEKLY,
            recurrence_interval=2,
            due_date=date(2026, 3, 1),
        )

        next_task = generate_next_occurrence(task)
        assert next_task.due_date == date(2026, 3, 15)


class TestCompleteTaskRecurrence:
    def test_completing_recurring_task_creates_next_occurrence(self, auth_client, user):
        task = Task.objects.create(
            user=user,
            title='Water the plants',
            recurrence=RecurrenceRule.WEEKLY,
            recurrence_interval=1,
            due_date=date(2026, 3, 1),
        )

        response = auth_client.post(reverse('task-complete', kwargs={'task_id': task.id}))
        assert response.status_code == 200

        assert Task.objects.filter(user=user, title='Water the plants').count() == 2
        new_task = Task.objects.exclude(id=task.id).get(user=user, title='Water the plants')
        assert new_task.due_date == date(2026, 3, 8)
        assert new_task.is_completed is False
        assert new_task.recurrence_parent_id == task.id

    def test_completing_non_recurring_task_creates_nothing_extra(self, auth_client, user):
        task = Task.objects.create(user=user, title='One-off errand')

        response = auth_client.post(reverse('task-complete', kwargs={'task_id': task.id}))
        assert response.status_code == 200

        assert Task.objects.filter(user=user).count() == 1

    def test_completing_already_completed_task_is_idempotent(self, auth_client, user):
        task = Task.objects.create(
            user=user,
            title='Water the plants',
            recurrence=RecurrenceRule.WEEKLY,
            is_completed=True,
        )

        response = auth_client.post(reverse('task-complete', kwargs={'task_id': task.id}))
        assert response.status_code == 200

        # No second occurrence generated for a task that was already complete.
        assert Task.objects.filter(user=user).count() == 1
