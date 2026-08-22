"""
Celery tasks — Analytics & Insights (ARCHITECTURE.md Section 8: background
jobs).

Task bodies are intentionally thin: they delegate to services.py, mirroring
apps/notifications/tasks.py and apps/family/tasks.py.
"""

from celery import shared_task


@shared_task(name='analytics.generate_weekly_reports')
def generate_weekly_reports_task() -> int:
    """Celery Beat periodic task (see settings.CELERY_BEAT_SCHEDULE) — the
    Milestone 11 "Progress reports generated on a sensible cadence (e.g.,
    weekly)" requirement. Generates the past week's progress report for
    every active user who doesn't already have one for that period.
    Returns the number of reports generated."""
    from apps.analytics.services import generate_weekly_reports_for_all_users

    return generate_weekly_reports_for_all_users()
