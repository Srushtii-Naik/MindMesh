"""Tests for apps.analytics.tasks — a thin Celery wrapper around the
service already covered in test_progress_reports.py.
CELERY_TASK_ALWAYS_EAGER=True (config/settings/test.py) makes this run
synchronously in-process."""

import pytest

from apps.analytics.models import ProgressReport
from apps.analytics.tasks import generate_weekly_reports_task

pytestmark = pytest.mark.django_db


def test_generate_weekly_reports_task_creates_reports_for_active_users(user, other_user):
    generated = generate_weekly_reports_task()

    assert generated == 2
    assert ProgressReport.objects.filter(user=user).exists()
    assert ProgressReport.objects.filter(user=other_user).exists()


def test_generate_weekly_reports_task_is_idempotent(user):
    generate_weekly_reports_task()
    generate_weekly_reports_task()

    assert ProgressReport.objects.filter(user=user).count() == 1
