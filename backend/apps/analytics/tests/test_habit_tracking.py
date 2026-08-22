"""Tests for apps.analytics.services.get_habit_tracking (ROADMAP.md
Milestone 11: "Habit tracking implemented and visualized clearly")."""

from datetime import timedelta

import pytest
from django.utils import timezone

from apps.analytics.services import get_habit_tracking

pytestmark = pytest.mark.django_db


class TestHabitTracking:
    def test_empty_state_has_zero_streaks(self, user):
        habits = get_habit_tracking(user, days=14)

        assert habits['current_streak_days'] == 0
        assert habits['longest_streak_days'] == 0
        assert all(not day['is_active_day'] for day in habits['daily_activity'])

    def test_current_streak_counts_consecutive_days_ending_today(
        self, user, completed_task_factory
    ):
        today = timezone.localdate()
        completed_task_factory(on_date=today)
        completed_task_factory(on_date=today - timedelta(days=1))
        completed_task_factory(on_date=today - timedelta(days=2))

        habits = get_habit_tracking(user, days=14)

        assert habits['current_streak_days'] == 3

    def test_current_streak_is_zero_if_today_has_no_completion(
        self, user, completed_task_factory
    ):
        today = timezone.localdate()
        completed_task_factory(on_date=today - timedelta(days=1))

        habits = get_habit_tracking(user, days=14)

        assert habits['current_streak_days'] == 0

    def test_streak_breaks_on_a_gap_day(self, user, completed_task_factory):
        today = timezone.localdate()
        completed_task_factory(on_date=today)
        # Gap at today - 1
        completed_task_factory(on_date=today - timedelta(days=2))

        habits = get_habit_tracking(user, days=14)

        assert habits['current_streak_days'] == 1

    def test_longest_streak_can_exceed_current_streak(self, user, completed_task_factory):
        today = timezone.localdate()
        # A 3-day streak in the past, then a gap, then today alone.
        completed_task_factory(on_date=today - timedelta(days=10))
        completed_task_factory(on_date=today - timedelta(days=9))
        completed_task_factory(on_date=today - timedelta(days=8))
        completed_task_factory(on_date=today)

        habits = get_habit_tracking(user, days=14)

        assert habits['current_streak_days'] == 1
        assert habits['longest_streak_days'] == 3

    def test_daily_activity_marks_correct_days_active(self, user, completed_task_factory):
        today = timezone.localdate()
        completed_task_factory(on_date=today)

        habits = get_habit_tracking(user, days=3)

        today_point = next(d for d in habits['daily_activity'] if d['date'] == today)
        assert today_point['is_active_day'] is True

    def test_isolated_per_user(self, user, other_user, completed_task_factory):
        completed_task_factory(on_date=timezone.localdate())

        other_habits = get_habit_tracking(other_user, days=14)

        assert other_habits['current_streak_days'] == 0
