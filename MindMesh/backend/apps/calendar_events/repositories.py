"""
Repository / data-access layer — Calendar & Scheduling.

Encapsulates ORM queries for Event, isolating persistence details from the
service layer, per ARCHITECTURE.md Section 3. Every query here is scoped to
a given user — row-level ownership per PROJECT_RULES.md Section 7.
"""

from datetime import date, datetime

from django.db.models import QuerySet
from django.utils import timezone

from apps.accounts.models import User
from apps.calendar_events.models import Event


def list_events_for_user(user: User) -> QuerySet[Event]:
    """Base queryset of the user's non-deleted events. Filters applied by the service layer."""
    return Event.objects.filter(user=user, is_active=True)


def get_event_for_user(user: User, event_id) -> Event | None:
    return Event.objects.filter(user=user, id=event_id, is_active=True).first()


def create_event(*, user: User, **fields) -> Event:
    return Event.objects.create(user=user, **fields)


def update_event(event: Event, **fields) -> Event:
    for field, value in fields.items():
        setattr(event, field, value)
    event.save()
    return event


def soft_delete_event(event: Event) -> None:
    event.is_active = False
    event.deleted_at = timezone.now()
    event.save(update_fields=['is_active', 'deleted_at', 'updated_at'])


def list_events_overlapping_range(
    user: User, range_start: datetime, range_end: datetime
) -> QuerySet[Event]:
    """Events whose [start_time, end_time] window overlaps [range_start, range_end]."""
    return list_events_for_user(user).filter(
        start_time__lte=range_end, end_time__gte=range_start
    )


def list_events_for_day(user: User, target_date: date) -> QuerySet[Event]:
    day_start = datetime.combine(target_date, datetime.min.time(), tzinfo=timezone.get_current_timezone())
    day_end = datetime.combine(target_date, datetime.max.time(), tzinfo=timezone.get_current_timezone())
    return list_events_overlapping_range(user, day_start, day_end)
