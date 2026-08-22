"""Tests for apps.analytics.services progress-report generation
(ROADMAP.md Milestone 11: "Progress reports generated on a sensible
cadence (e.g., weekly)")."""

from datetime import timedelta

import pytest
from django.utils import timezone

from apps.analytics.models import ProgressReport
from apps.analytics.services import (
    ReportNotFoundError,
    generate_progress_report_for_user,
    generate_weekly_reports_for_all_users,
    get_progress_report,
    list_progress_reports,
)

pytestmark = pytest.mark.django_db


class TestGenerateProgressReport:
    def test_creates_a_report_with_correct_stats(self, user, completed_task_factory):
        today = timezone.localdate()
        start = today - timedelta(days=6)
        completed_task_factory(on_date=today)
        completed_task_factory(on_date=today - timedelta(days=1))

        report = generate_progress_report_for_user(user, period_start=start, period_end=today)

        assert report.tasks_completed == 2
        assert report.period_start == start
        assert report.period_end == today

    def test_is_idempotent_for_the_same_period(self, user, completed_task_factory):
        today = timezone.localdate()
        start = today - timedelta(days=6)
        completed_task_factory(on_date=today)

        first = generate_progress_report_for_user(user, period_start=start, period_end=today)
        second = generate_progress_report_for_user(user, period_start=start, period_end=today)

        assert first.id == second.id
        assert ProgressReport.objects.filter(user=user).count() == 1

    def test_force_regenerates_the_report(self, user, completed_task_factory):
        today = timezone.localdate()
        start = today - timedelta(days=6)
        completed_task_factory(on_date=today)

        first = generate_progress_report_for_user(user, period_start=start, period_end=today)
        completed_task_factory(on_date=today - timedelta(days=1))
        second = generate_progress_report_for_user(
            user, period_start=start, period_end=today, force=True
        )

        assert second.tasks_completed == 2
        assert ProgressReport.objects.filter(user=user).count() == 1
        assert first.id != second.id

    def test_includes_an_ai_summary_via_stub_provider(self, user, completed_task_factory):
        today = timezone.localdate()
        completed_task_factory(on_date=today)

        report = generate_progress_report_for_user(
            user, period_start=today - timedelta(days=6), period_end=today
        )

        assert isinstance(report.ai_summary, str)

    def test_ai_summary_blank_on_provider_failure(self, user, monkeypatch):
        from apps.ai_companion import services as ai_services
        from apps.ai_companion.providers import AIProviderError

        class _FailingProvider:
            def generate_response(self, *args, **kwargs):
                raise AIProviderError('provider unavailable')

        monkeypatch.setattr(ai_services, 'get_ai_provider', lambda: _FailingProvider())

        today = timezone.localdate()
        report = generate_progress_report_for_user(
            user, period_start=today - timedelta(days=6), period_end=today
        )

        assert report.ai_summary == ''


class TestGenerateWeeklyReportsForAllUsers:
    def test_generates_a_report_for_each_active_user(self, user, other_user):
        generated = generate_weekly_reports_for_all_users()

        assert generated == 2
        assert ProgressReport.objects.filter(user=user).count() == 1
        assert ProgressReport.objects.filter(user=other_user).count() == 1

    def test_does_not_duplicate_an_existing_period(self, user, other_user):
        generate_weekly_reports_for_all_users()
        generated_again = generate_weekly_reports_for_all_users()

        assert generated_again == 0
        assert ProgressReport.objects.filter(user=user).count() == 1

    def test_skips_inactive_users(self, user, other_user):
        other_user.is_active = False
        other_user.save(update_fields=['is_active'])

        generated = generate_weekly_reports_for_all_users()

        assert generated == 1
        assert ProgressReport.objects.filter(user=other_user).count() == 0


class TestListAndGetProgressReports:
    def test_list_returns_users_reports_most_recent_first(self, user):
        today = timezone.localdate()
        older = generate_progress_report_for_user(
            user, period_start=today - timedelta(days=13), period_end=today - timedelta(days=7)
        )
        newer = generate_progress_report_for_user(
            user, period_start=today - timedelta(days=6), period_end=today
        )

        reports = list(list_progress_reports(user))

        assert reports[0].id == newer.id
        assert reports[1].id == older.id

    def test_list_is_isolated_per_user(self, user, other_user):
        today = timezone.localdate()
        generate_progress_report_for_user(
            user, period_start=today - timedelta(days=6), period_end=today
        )

        assert list(list_progress_reports(other_user)) == []

    def test_get_progress_report_raises_when_not_found(self, user):
        import uuid

        with pytest.raises(ReportNotFoundError):
            get_progress_report(user, uuid.uuid4())

    def test_get_progress_report_does_not_leak_across_users(self, user, other_user):
        today = timezone.localdate()
        report = generate_progress_report_for_user(
            user, period_start=today - timedelta(days=6), period_end=today
        )

        with pytest.raises(ReportNotFoundError):
            get_progress_report(other_user, report.id)
