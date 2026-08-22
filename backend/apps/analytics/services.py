"""
Service layer — Analytics & Insights.

Domain business logic for productivity analytics, habit tracking,
AI-generated recommendations, and progress reports (ROADMAP.md Milestone
11). Per ARCHITECTURE.md Section 3: views call services; services never
import DRF.

Every other domain's data (tasks, notes, calendar events) is read only
through its own service-layer entry point — apps.tasks.services,
apps.notes.services, apps.calendar_events.services — never by importing
their models directly, mirroring the existing cross-domain pattern (e.g.
apps.calendar_events.services calling apps.tasks.services.get_tasks_due_between)
per ARCHITECTURE.md Section 3. AI recommendations are generated through
apps.ai_companion.services.generate_recommendation_text, the sole path to
the AI abstraction layer for this domain, per PROJECT_RULES.md Section 10.
"""

from __future__ import annotations

import re
from datetime import date, timedelta

from django.core.cache import cache
from django.utils import timezone

from apps.accounts.models import User
from apps.ai_companion.services import RecommendationError, generate_recommendation_text
from apps.analytics.models import ProgressReport
from apps.analytics.repositories import (
    create_progress_report,
    get_progress_report_for_period,
    get_progress_report_for_user,
    list_progress_reports_for_user,
    report_exists_for_period,
)
from apps.calendar_events.services import get_event_count_for_range
from apps.notes.services import get_note_count_for_range
from apps.tasks.services import get_completed_dates_for_streak, get_task_productivity_stats

# Default lookback windows. Kept short/bounded so analytics stay fast and
# the AI-recommendation digest stays privacy-minimal (PROJECT_RULES.md
# Section 10 & 11).
DEFAULT_PRODUCTIVITY_WINDOW_DAYS = 30
DEFAULT_HABIT_WINDOW_DAYS = 90
RECOMMENDATION_DIGEST_WINDOW_DAYS = 14
RECOMMENDATION_STREAK_WINDOW_DAYS = 30
MAX_RECOMMENDATIONS = 4

# Cache AI-generated recommendations per user (PROJECT_RULES.md Section 11:
# "Redis caching... AI responses for repeated queries... to reduce database
# and AI provider load"). Recommendations are advisory and don't need to be
# real-time, so an hour-long TTL is a reasonable trade-off.
RECOMMENDATIONS_CACHE_TTL_SECONDS = 3600


class ReportNotFoundError(Exception):
    """Raised when a progress report cannot be found for the requesting user."""


# --------------------------------------------------------------------------
# Productivity analytics (ROADMAP.md Milestone 11:
# "Productivity analytics computed accurately from task/calendar data")
# --------------------------------------------------------------------------


def _date_range(start_date: date, end_date: date):
    current = start_date
    while current <= end_date:
        yield current
        current += timedelta(days=1)


def _build_daily_series(
    start_date: date, end_date: date, completed_by_day: dict, created_by_day: dict
) -> list[dict]:
    return [
        {
            'date': day,
            'tasks_completed': completed_by_day.get(day, 0),
            'tasks_created': created_by_day.get(day, 0),
        }
        for day in _date_range(start_date, end_date)
    ]


def get_productivity_analytics(
    user: User, *, days: int = DEFAULT_PRODUCTIVITY_WINDOW_DAYS
) -> dict:
    """Powers GET /api/v1/analytics/productivity/ — task completion rate,
    totals, and a day-by-day series, plus cross-module counts (notes
    created, events scheduled) for the same window, per ARCHITECTURE.md
    Section 4's "AI & Memory... future embeddings" entity group being kept
    separate from this Milestone's plain aggregate stats."""
    end_date = timezone.localdate()
    start_date = end_date - timedelta(days=days - 1)

    task_stats = get_task_productivity_stats(user, start_date, end_date)

    return {
        'period_start': start_date,
        'period_end': end_date,
        'tasks_created': task_stats['tasks_created'],
        'tasks_completed': task_stats['tasks_completed'],
        'completion_rate': task_stats['completion_rate'],
        'notes_created': get_note_count_for_range(user, start_date, end_date),
        'events_scheduled': get_event_count_for_range(user, start_date, end_date),
        'daily_series': _build_daily_series(
            start_date, end_date, task_stats['completed_by_day'], task_stats['created_by_day']
        ),
    }


# --------------------------------------------------------------------------
# Habit tracking (ROADMAP.md Milestone 11:
# "Habit tracking implemented and visualized clearly")
# --------------------------------------------------------------------------


def _current_streak(completed_dates: set[date], as_of: date) -> int:
    streak = 0
    day = as_of
    while day in completed_dates:
        streak += 1
        day -= timedelta(days=1)
    return streak


def _longest_streak(completed_dates: set[date], start_date: date, end_date: date) -> int:
    longest = 0
    running = 0
    for day in _date_range(start_date, end_date):
        if day in completed_dates:
            running += 1
            longest = max(longest, running)
        else:
            running = 0
    return longest


def get_habit_tracking(user: User, *, days: int = DEFAULT_HABIT_WINDOW_DAYS) -> dict:
    """Powers GET /api/v1/analytics/habits/ — a daily-completion "did I get
    something done today" streak, visualized as a calendar heatmap on the
    frontend. Deliberately built on the task-completion data that already
    exists rather than introducing a separate habit-definition model —
    PROJECT_RULES.md Section 1: "Simplicity over feature overload... every
    added feature is a tax... When in doubt, leave it out.\""""
    end_date = timezone.localdate()
    start_date = end_date - timedelta(days=days - 1)

    completed_dates = get_completed_dates_for_streak(user, start_date, end_date)

    return {
        'period_start': start_date,
        'period_end': end_date,
        'current_streak_days': _current_streak(completed_dates, end_date),
        'longest_streak_days': _longest_streak(completed_dates, start_date, end_date),
        'daily_activity': [
            {'date': day, 'is_active_day': day in completed_dates}
            for day in _date_range(start_date, end_date)
        ],
    }


# --------------------------------------------------------------------------
# AI-generated recommendations (ROADMAP.md Milestone 11: "AI-generated
# recommendations surfaced through the AI abstraction layer")
# --------------------------------------------------------------------------


def _build_recommendation_digest(user: User) -> str:
    """A compact, natural-language digest of the user's recent productivity
    — never a raw data dump, per PROJECT_RULES.md Section 10 ("Privacy-first
    AI... scoped and minimized"). Mirrors the shape of
    apps.ai_companion.services.assemble_context_for_user without reusing it
    directly, since that function is chat-specific (conversation history +
    memory facts), while this is a pure analytics digest."""
    productivity = get_productivity_analytics(user, days=RECOMMENDATION_DIGEST_WINDOW_DAYS)
    habits = get_habit_tracking(user, days=RECOMMENDATION_STREAK_WINDOW_DAYS)

    lines = [
        f"Over the last {RECOMMENDATION_DIGEST_WINDOW_DAYS} days: "
        f"{productivity['tasks_completed']} of {productivity['tasks_created']} tasks "
        f"completed ({productivity['completion_rate']}% completion rate).",
        f"{productivity['notes_created']} note(s) written and "
        f"{productivity['events_scheduled']} calendar event(s) scheduled in that time.",
        f"Current daily task-completion streak: {habits['current_streak_days']} day(s); "
        f"longest streak in the last {RECOMMENDATION_STREAK_WINDOW_DAYS} days: "
        f"{habits['longest_streak_days']} day(s).",
    ]
    return ' '.join(lines)


def _split_into_recommendations(raw: str) -> list[str]:
    cleaned = (raw or '').strip()
    if not cleaned:
        return []

    lines = [line.strip(' -*•\t') for line in cleaned.splitlines() if line.strip()]
    if len(lines) > 1:
        return [line for line in lines if line][:MAX_RECOMMENDATIONS]

    # A single-paragraph reply — split into sentences instead.
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', cleaned) if s.strip()]
    return sentences[:MAX_RECOMMENDATIONS]


def get_ai_recommendations(user: User, *, use_cache: bool = True) -> list[str]:
    """Powers GET /api/v1/analytics/recommendations/. Routed exclusively
    through apps.ai_companion.services (the AI abstraction layer's
    cross-domain entry point) — never a direct provider call, per
    PROJECT_RULES.md Section 10. Falls back to an empty list (rather than
    raising) on provider failure, since recommendations are advisory, not
    load-bearing — mirroring apps.tasks.services.get_ai_enhanced_suggestions'
    graceful-degradation behavior."""
    cache_key = f'analytics:recommendations:{user.id}'
    if use_cache:
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

    digest = _build_recommendation_digest(user)
    prompt = (
        'Based on the productivity summary below, suggest up to 3 short, specific, '
        'encouraging recommendations to help the person stay on track this week. '
        'One short sentence per recommendation, no numbering, no preamble.'
    )

    try:
        raw = generate_recommendation_text(prompt, context=digest)
    except RecommendationError:
        return []

    recommendations = _split_into_recommendations(raw)
    if use_cache:
        cache.set(cache_key, recommendations, RECOMMENDATIONS_CACHE_TTL_SECONDS)
    return recommendations


# --------------------------------------------------------------------------
# Progress reports (ROADMAP.md Milestone 11:
# "Progress reports generated on a sensible cadence (e.g., weekly)")
# --------------------------------------------------------------------------


def list_progress_reports(user: User, *, limit: int = 12):
    return list_progress_reports_for_user(user, limit=limit)


def get_progress_report(user: User, report_id) -> ProgressReport:
    report = get_progress_report_for_user(user, report_id)
    if report is None:
        raise ReportNotFoundError('Progress report not found.')
    return report


def _generate_report_summary(productivity: dict, habits: dict) -> str:
    """A short, encouraging natural-language summary for the report, via
    the AI abstraction layer. Returns '' on failure — a report without an
    AI summary is still a complete, useful report."""
    digest = (
        f"{productivity['tasks_completed']} of {productivity['tasks_created']} tasks "
        f"completed ({productivity['completion_rate']}% completion rate). "
        f"{productivity['notes_created']} note(s), {productivity['events_scheduled']} "
        f"calendar event(s). Longest daily task-completion streak this period: "
        f"{habits['longest_streak_days']} day(s)."
    )
    prompt = (
        'Write one short, warm, encouraging sentence summarizing this week\'s progress '
        'for the person, based on the stats below. No preamble, just the sentence.'
    )
    try:
        return generate_recommendation_text(prompt, context=digest).strip()
    except RecommendationError:
        return ''


def generate_progress_report_for_user(
    user: User, *, period_start: date, period_end: date, force: bool = False
) -> ProgressReport:
    """Generates (or returns the existing) progress report for the given
    period. Idempotent by default — regenerating an already-generated
    period is a no-op, enforced by the model's unique constraint and
    checked here first to avoid an avoidable AI-provider call."""
    existing = get_progress_report_for_period(user, period_start, period_end)
    if existing is not None:
        if not force:
            return existing
        existing.delete()

    task_stats = get_task_productivity_stats(user, period_start, period_end)
    completed_dates = get_completed_dates_for_streak(user, period_start, period_end)
    notes_created = get_note_count_for_range(user, period_start, period_end)
    events_scheduled = get_event_count_for_range(user, period_start, period_end)

    productivity = {
        'tasks_created': task_stats['tasks_created'],
        'tasks_completed': task_stats['tasks_completed'],
        'completion_rate': task_stats['completion_rate'],
        'notes_created': notes_created,
        'events_scheduled': events_scheduled,
    }
    habits = {
        'current_streak_days': _current_streak(completed_dates, period_end),
        'longest_streak_days': _longest_streak(completed_dates, period_start, period_end),
    }

    return create_progress_report(
        user=user,
        period_start=period_start,
        period_end=period_end,
        tasks_created=productivity['tasks_created'],
        tasks_completed=productivity['tasks_completed'],
        completion_rate=productivity['completion_rate'],
        notes_created=notes_created,
        events_scheduled=events_scheduled,
        current_streak_days=habits['current_streak_days'],
        longest_streak_days=habits['longest_streak_days'],
        ai_summary=_generate_report_summary(productivity, habits),
    )


def generate_weekly_reports_for_all_users() -> int:
    """Celery Beat entry point (apps.analytics.tasks) — generates the past
    week's progress report for every active user who doesn't already have
    one for that exact period. Returns the number of reports generated."""
    today = timezone.localdate()
    period_end = today - timedelta(days=1)  # the most recently completed day
    period_start = period_end - timedelta(days=6)  # a 7-day window

    generated = 0
    for user in User.objects.filter(is_active=True):
        if report_exists_for_period(user, period_start, period_end):
            continue
        generate_progress_report_for_user(user, period_start=period_start, period_end=period_end)
        generated += 1

    return generated
