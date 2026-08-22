from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from apps.tasks.models import Priority, SubTask, Task

pytestmark = pytest.mark.django_db


class TestSuggestions:
    def test_no_suggestions_for_empty_task_list(self, auth_client):
        response = auth_client.get(reverse('task-suggestions'))
        assert response.status_code == 200
        assert response.json() == []

    def test_overdue_suggestion(self, auth_client, user):
        yesterday = timezone.localdate() - timedelta(days=1)
        Task.objects.create(user=user, title='Late task', due_date=yesterday)

        response = auth_client.get(reverse('task-suggestions'))

        kinds = [item['kind'] for item in response.json()]
        assert 'overdue' in kinds

    def test_due_today_suggestion(self, auth_client, user):
        Task.objects.create(user=user, title='Today task', due_date=timezone.localdate())

        response = auth_client.get(reverse('task-suggestions'))

        kinds = [item['kind'] for item in response.json()]
        assert 'due_today' in kinds

    def test_missing_due_date_suggestion_for_high_priority(self, auth_client, user):
        Task.objects.create(user=user, title='Important but undated', priority=Priority.URGENT)

        response = auth_client.get(reverse('task-suggestions'))

        kinds = [item['kind'] for item in response.json()]
        assert 'missing_due_date' in kinds

    def test_no_missing_due_date_suggestion_for_low_priority(self, auth_client, user):
        Task.objects.create(user=user, title='Low priority, no date', priority=Priority.LOW)

        response = auth_client.get(reverse('task-suggestions'))

        kinds = [item['kind'] for item in response.json()]
        assert 'missing_due_date' not in kinds

    def test_ready_to_complete_suggestion(self, auth_client, user):
        task = Task.objects.create(user=user, title='Almost done')
        SubTask.objects.create(task=task, title='Step 1', is_completed=True)
        SubTask.objects.create(task=task, title='Step 2', is_completed=True)

        response = auth_client.get(reverse('task-suggestions'))

        kinds = [item['kind'] for item in response.json()]
        assert 'ready_to_complete' in kinds

    def test_no_ready_to_complete_suggestion_when_a_subtask_is_incomplete(self, auth_client, user):
        task = Task.objects.create(user=user, title='Not quite done')
        SubTask.objects.create(task=task, title='Step 1', is_completed=True)
        SubTask.objects.create(task=task, title='Step 2', is_completed=False)

        response = auth_client.get(reverse('task-suggestions'))

        kinds = [item['kind'] for item in response.json()]
        assert 'ready_to_complete' not in kinds

    def test_suggestions_only_reflect_own_tasks(self, auth_client, other_user):
        yesterday = timezone.localdate() - timedelta(days=1)
        Task.objects.create(user=other_user, title='Not mine', due_date=yesterday)

        response = auth_client.get(reverse('task-suggestions'))
        assert response.json() == []


class TestTodaySummary:
    def test_summary_counts(self, auth_client, user):
        today = timezone.localdate()
        yesterday = today - timedelta(days=1)

        Task.objects.create(user=user, title='Due today', due_date=today)
        Task.objects.create(user=user, title='Overdue', due_date=yesterday)
        Task.objects.create(
            user=user, title='Done today', is_completed=True, completed_at=timezone.now()
        )

        response = auth_client.get(reverse('task-today-summary'))

        assert response.status_code == 200
        body = response.json()
        assert body['due_today_count'] == 1
        assert body['overdue_count'] == 1
        assert body['completed_today_count'] == 1

    def test_summary_requires_authentication(self, api_client):
        response = api_client.get(reverse('task-today-summary'))
        assert response.status_code == 401
