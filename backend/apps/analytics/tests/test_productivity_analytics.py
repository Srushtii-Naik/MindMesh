"""Tests for apps.analytics.services.get_productivity_analytics
(ROADMAP.md Milestone 11: "Productivity analytics computed accurately
from task/calendar data")."""

from datetime import timedelta

import pytest
from django.utils import timezone

from apps.analytics.services import get_productivity_analytics
from apps.calendar_events.models import Event
from apps.notes.models import Note

pytestmark = pytest.mark.django_db


class TestProductivityAnalytics:
    def test_empty_state_returns_zeroed_stats(self, user):
        analytics = get_productivity_analytics(user, days=7)

        assert analytics['tasks_created'] == 0
        assert analytics['tasks_completed'] == 0
        assert analytics['completion_rate'] == 0.0
        assert analytics['notes_created'] == 0
        assert analytics['events_scheduled'] == 0
        assert len(analytics['daily_series']) == 7

    def test_counts_tasks_created_and_completed_within_window(
        self, user, completed_task_factory, created_task_factory
    ):
        today = timezone.localdate()
        completed_task_factory(on_date=today)
        completed_task_factory(on_date=today - timedelta(days=1))
        created_task_factory(on_date=today)

        analytics = get_productivity_analytics(user, days=7)

        assert analytics['tasks_completed'] == 2
        # 2 completed tasks + 1 incomplete task = 3 created in-window
        assert analytics['tasks_created'] == 3

    def test_completion_rate_is_percentage_of_created(
        self, user, completed_task_factory, created_task_factory
    ):
        today = timezone.localdate()
        completed_task_factory(on_date=today)
        created_task_factory(on_date=today)

        analytics = get_productivity_analytics(user, days=7)

        assert analytics['tasks_created'] == 2
        assert analytics['tasks_completed'] == 1
        assert analytics['completion_rate'] == 50.0

    def test_excludes_activity_outside_the_window(self, user, completed_task_factory):
        today = timezone.localdate()
        completed_task_factory(on_date=today - timedelta(days=30))

        analytics = get_productivity_analytics(user, days=7)

        assert analytics['tasks_completed'] == 0

    def test_daily_series_places_counts_on_correct_day(self, user, completed_task_factory):
        today = timezone.localdate()
        completed_task_factory(on_date=today)

        analytics = get_productivity_analytics(user, days=3)

        today_point = next(p for p in analytics['daily_series'] if p['date'] == today)
        assert today_point['tasks_completed'] == 1

    def test_counts_notes_created_in_window(self, user):
        Note.objects.create(user=user, title='A note', content='Body')

        analytics = get_productivity_analytics(user, days=7)

        assert analytics['notes_created'] == 1

    def test_counts_events_scheduled_in_window(self, user):
        now = timezone.now()
        Event.objects.create(
            user=user, title='Standup', start_time=now, end_time=now + timedelta(hours=1)
        )

        analytics = get_productivity_analytics(user, days=7)

        assert analytics['events_scheduled'] == 1

    def test_isolated_per_user(self, user, other_user, completed_task_factory):
        completed_task_factory(on_date=timezone.localdate())

        other_analytics = get_productivity_analytics(other_user, days=7)

        assert other_analytics['tasks_completed'] == 0
