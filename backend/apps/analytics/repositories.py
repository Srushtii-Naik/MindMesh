"""
Repository / data-access layer — Analytics & Insights.

Encapsulates ORM queries for ProgressReport, isolating persistence details
from the service layer, per ARCHITECTURE.md Section 3. Every query here is
scoped to a given user — row-level ownership per PROJECT_RULES.md Section 7.
"""

from datetime import date

from django.db.models import QuerySet

from apps.accounts.models import User
from apps.analytics.models import ProgressReport

DEFAULT_REPORT_HISTORY_LIMIT = 12


def list_progress_reports_for_user(
    user: User, *, limit: int = DEFAULT_REPORT_HISTORY_LIMIT
) -> QuerySet[ProgressReport]:
    return ProgressReport.objects.filter(user=user)[:limit]


def get_progress_report_for_user(user: User, report_id) -> ProgressReport | None:
    return ProgressReport.objects.filter(user=user, id=report_id).first()


def get_latest_progress_report_for_user(user: User) -> ProgressReport | None:
    return ProgressReport.objects.filter(user=user).order_by('-period_end').first()


def report_exists_for_period(user: User, period_start: date, period_end: date) -> bool:
    return ProgressReport.objects.filter(
        user=user, period_start=period_start, period_end=period_end
    ).exists()


def get_progress_report_for_period(
    user: User, period_start: date, period_end: date
) -> ProgressReport | None:
    return ProgressReport.objects.filter(
        user=user, period_start=period_start, period_end=period_end
    ).first()


def create_progress_report(*, user: User, **fields) -> ProgressReport:
    return ProgressReport.objects.create(user=user, **fields)
