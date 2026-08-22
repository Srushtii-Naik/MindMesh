"""API-level tests for apps.analytics views — authentication requirements,
response shapes, and permission boundaries (PROJECT_RULES.md Section 12:
"Every endpoint's behavior... success paths, validation failures, and
permission boundaries... is covered by tests")."""

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from apps.analytics.services import generate_progress_report_for_user

pytestmark = pytest.mark.django_db


class TestProductivityAnalyticsView:
    def test_requires_authentication(self, api_client):
        response = api_client.get(reverse('analytics-productivity'))
        assert response.status_code == 401

    def test_returns_productivity_shape(self, auth_client):
        response = auth_client.get(reverse('analytics-productivity'))

        assert response.status_code == 200
        body = response.json()
        assert set(body.keys()) >= {
            'period_start', 'period_end', 'tasks_created', 'tasks_completed',
            'completion_rate', 'notes_created', 'events_scheduled', 'daily_series',
        }

    def test_respects_days_query_param(self, auth_client):
        response = auth_client.get(reverse('analytics-productivity'), {'days': 7})

        assert response.status_code == 200
        assert len(response.json()['daily_series']) == 7

    def test_rejects_invalid_days_param(self, auth_client):
        response = auth_client.get(reverse('analytics-productivity'), {'days': 0})
        assert response.status_code == 400

    def test_isolated_per_user(self, auth_client, user, completed_task_factory):
        completed_task_factory(on_date=timezone.localdate())

        response = auth_client.get(reverse('analytics-productivity'))
        assert response.json()['tasks_completed'] == 1


class TestHabitTrackingView:
    def test_requires_authentication(self, api_client):
        response = api_client.get(reverse('analytics-habits'))
        assert response.status_code == 401

    def test_returns_habit_shape(self, auth_client):
        response = auth_client.get(reverse('analytics-habits'))

        assert response.status_code == 200
        body = response.json()
        assert set(body.keys()) >= {
            'period_start', 'period_end', 'current_streak_days',
            'longest_streak_days', 'daily_activity',
        }


class TestRecommendationsView:
    def test_requires_authentication(self, api_client):
        response = api_client.get(reverse('analytics-recommendations'))
        assert response.status_code == 401

    def test_returns_recommendations_list(self, auth_client):
        response = auth_client.get(reverse('analytics-recommendations'))

        assert response.status_code == 200
        assert isinstance(response.json()['recommendations'], list)


class TestProgressReportViews:
    def test_list_requires_authentication(self, api_client):
        response = api_client.get(reverse('analytics-report-list'))
        assert response.status_code == 401

    def test_list_returns_users_reports(self, auth_client, user):
        today = timezone.localdate()
        generate_progress_report_for_user(
            user, period_start=today - timedelta(days=6), period_end=today
        )

        response = auth_client.get(reverse('analytics-report-list'))

        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_detail_returns_a_single_report(self, auth_client, user):
        today = timezone.localdate()
        report = generate_progress_report_for_user(
            user, period_start=today - timedelta(days=6), period_end=today
        )

        response = auth_client.get(
            reverse('analytics-report-detail', kwargs={'report_id': report.id})
        )

        assert response.status_code == 200
        assert response.json()['id'] == str(report.id)

    def test_detail_returns_404_for_unknown_report(self, auth_client):
        import uuid

        response = auth_client.get(
            reverse('analytics-report-detail', kwargs={'report_id': uuid.uuid4()})
        )
        assert response.status_code == 404

    def test_detail_does_not_leak_another_users_report(self, auth_client, other_user):
        today = timezone.localdate()
        other_report = generate_progress_report_for_user(
            other_user, period_start=today - timedelta(days=6), period_end=today
        )

        response = auth_client.get(
            reverse('analytics-report-detail', kwargs={'report_id': other_report.id})
        )
        assert response.status_code == 404
