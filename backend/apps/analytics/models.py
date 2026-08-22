"""
Domain models — Analytics & Insights.

Per ARCHITECTURE.md Section 4: every domain table is scoped to a user_id
with row-level ownership enforced at the service layer, and timestamps are
standardized across all tables.

`ProgressReport` is a system-generated, immutable snapshot (ROADMAP.md
Milestone 11: "Progress reports generated on a sensible cadence"), not
user-authored content, so it's hard-deleted rather than soft-deleted —
PROJECT_RULES.md Section 7's soft-delete rule is scoped to user-generated
content, which this isn't. All other Milestone 11 analytics (productivity
stats, habit streaks, AI recommendations) are computed on demand from the
existing Task/Note/Event data via cross-domain service entry points
(apps.tasks.services, apps.notes.services, apps.calendar_events.services)
rather than duplicated into their own tables here.
"""

import uuid

from django.conf import settings
from django.db import models


class ProgressReport(models.Model):
    """A generated snapshot of a user's productivity over a fixed period
    (ROADMAP.md Milestone 11: "Progress reports"). Regenerating a report for
    a period that already has one is a no-op at the service layer — see
    apps.analytics.services.generate_progress_report_for_user — enforced
    here by the unique constraint below."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='progress_reports'
    )

    period_start = models.DateField()
    period_end = models.DateField()

    tasks_created = models.PositiveIntegerField(default=0)
    tasks_completed = models.PositiveIntegerField(default=0)
    completion_rate = models.FloatField(default=0.0)
    notes_created = models.PositiveIntegerField(default=0)
    events_scheduled = models.PositiveIntegerField(default=0)
    current_streak_days = models.PositiveIntegerField(default=0)
    longest_streak_days = models.PositiveIntegerField(default=0)

    # Short, encouraging natural-language summary generated through the AI
    # abstraction layer (apps.ai_companion.services.generate_recommendation_text).
    # Blank when the provider call fails — a report is still useful without it.
    ai_summary = models.TextField(blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'analytics_progress_report'
        ordering = ['-period_end']
        verbose_name = 'progress report'
        verbose_name_plural = 'progress reports'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'period_start', 'period_end'],
                name='unique_progress_report_period_per_user',
            )
        ]
        indexes = [models.Index(fields=['user', 'period_end'])]

    def __str__(self) -> str:
        return f'{self.user_id} ({self.period_start} – {self.period_end})'
