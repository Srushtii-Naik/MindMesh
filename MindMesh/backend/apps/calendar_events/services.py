"""
Service layer — Calendar & Scheduling.

Domain business logic for events, the combined calendar view, and the
daily/weekly planners. Per ARCHITECTURE.md Section 3: views call services;
services never import DRF.

Task associations are resolved through apps.tasks.services (a service
interface), never by importing apps.tasks.models directly, per
ARCHITECTURE.md Section 3.
"""

from datetime import date, datetime, timedelta

from django.utils import timezone

from apps.accounts.models import User
from apps.calendar_events.models import Event
from apps.calendar_events.repositories import (
    create_event,
    get_event_for_user,
    list_events_for_day,
    list_events_for_user,
    list_events_overlapping_range,
    soft_delete_event,
    update_event,
)
from apps.tasks.services import TaskNotFoundError, get_tasks_due_between
from apps.tasks.services import get_task as get_task_for_user


class EventNotFoundError(Exception):
    """Raised when an event cannot be found for the requesting user."""


class InvalidEventRangeError(Exception):
    """Raised when an event's end_time is not after its start_time."""


class LinkedTaskNotFoundError(Exception):
    """Raised when an event is linked to a task the user doesn't own."""


# --------------------------------------------------------------------------
# Events
# --------------------------------------------------------------------------


def _resolve_task(user: User, task_id):
    if task_id is None:
        return None
    try:
        return get_task_for_user(user, task_id)
    except TaskNotFoundError as exc:
        raise LinkedTaskNotFoundError(str(exc)) from exc


def _validate_range(start_time: datetime, end_time: datetime) -> None:
    if end_time <= start_time:
        raise InvalidEventRangeError('End time must be after start time.')


def get_event(user: User, event_id) -> Event:
    event = get_event_for_user(user, event_id)
    if event is None:
        raise EventNotFoundError('Event not found.')
    return event


def list_events_for_user_filtered(
    user: User,
    *,
    start: datetime | None = None,
    end: datetime | None = None,
    task_id=None,
    search: str | None = None,
):
    """Filterable event listing. When both `start` and `end` are given, returns
    events whose window overlaps that range (ROADMAP.md Milestone 5: "Event CRUD
    implemented and validated")."""
    if start is not None and end is not None:
        queryset = list_events_overlapping_range(user, start, end)
    else:
        queryset = list_events_for_user(user)
        if start is not None:
            queryset = queryset.filter(end_time__gte=start)
        if end is not None:
            queryset = queryset.filter(start_time__lte=end)

    if task_id:
        queryset = queryset.filter(task_id=task_id)
    if search:
        queryset = queryset.filter(title__icontains=search)

    return queryset


def create_event_for_user(
    user: User,
    *,
    title: str,
    start_time: datetime,
    end_time: datetime,
    description: str = '',
    location: str = '',
    all_day: bool = False,
    color: str = '#5f6dfa',
    task_id=None,
) -> Event:
    _validate_range(start_time, end_time)
    task = _resolve_task(user, task_id)

    return create_event(
        user=user,
        title=title.strip(),
        description=description,
        location=location,
        start_time=start_time,
        end_time=end_time,
        all_day=all_day,
        color=color,
        task=task,
    )


def update_event_for_user(user: User, event_id, **fields) -> Event:
    event = get_event_for_user(user, event_id)
    if event is None:
        raise EventNotFoundError('Event not found.')

    if 'task_id' in fields:
        fields['task'] = _resolve_task(user, fields.pop('task_id'))
    if 'title' in fields:
        fields['title'] = fields['title'].strip()

    start_time = fields.get('start_time', event.start_time)
    end_time = fields.get('end_time', event.end_time)
    _validate_range(start_time, end_time)

    return update_event(event, **fields)


def delete_event_for_user(user: User, event_id) -> None:
    event = get_event_for_user(user, event_id)
    if event is None:
        raise EventNotFoundError('Event not found.')
    soft_delete_event(event)


# --------------------------------------------------------------------------
# Combined calendar view (events + task due dates, per ARCHITECTURE.md
# Section 4 and ROADMAP.md Milestone 5: "Calendar reflects task due dates
# and recurring tasks accurately")
# --------------------------------------------------------------------------


def _day_bounds(target_date: date) -> tuple[datetime, datetime]:
    tz = timezone.get_current_timezone()
    day_start = datetime.combine(target_date, datetime.min.time(), tzinfo=tz)
    day_end = datetime.combine(target_date, datetime.max.time(), tzinfo=tz)
    return day_start, day_end


def get_calendar_view(user: User, start_date: date, end_date: date) -> dict:
    """Powers month/range calendar rendering: events overlapping the range,
    plus tasks due within it."""
    range_start, _ = _day_bounds(start_date)
    _, range_end = _day_bounds(end_date)

    events = list_events_overlapping_range(user, range_start, range_end)
    tasks = get_tasks_due_between(user, start_date, end_date)

    return {'events': events, 'tasks': tasks}


def get_daily_planner(user: User, target_date: date) -> dict:
    """Powers the daily planner (ROADMAP.md Milestone 5)."""
    events = list_events_for_day(user, target_date)
    tasks = get_tasks_due_between(user, target_date, target_date)
    return {'date': target_date, 'events': events, 'tasks': tasks}


def get_weekly_planner(user: User, week_start: date) -> dict:
    """Powers the weekly planner (ROADMAP.md Milestone 5). `week_start` is the
    first day of the 7-day window shown (frontend decides Monday vs. Sunday)."""
    week_end = week_start + timedelta(days=6)
    view = get_calendar_view(user, week_start, week_end)
    events = list(view['events'])
    tasks = list(view['tasks'])

    days = []
    for offset in range(7):
        current_date = week_start + timedelta(days=offset)
        day_start, day_end = _day_bounds(current_date)
        day_events = [e for e in events if e.start_time <= day_end and e.end_time >= day_start]
        day_tasks = [t for t in tasks if t.due_date == current_date]
        days.append({'date': current_date, 'events': day_events, 'tasks': day_tasks})

    return {'week_start': week_start, 'week_end': week_end, 'days': days}
