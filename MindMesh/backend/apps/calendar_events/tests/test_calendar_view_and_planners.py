import datetime as dt

import pytest
from django.urls import reverse
from django.utils import timezone

pytestmark = pytest.mark.django_db


def _dt(day_offset=0, hour=9):
    base = timezone.now().replace(hour=hour, minute=0, second=0, microsecond=0)
    return base + timezone.timedelta(days=day_offset)


def test_calendar_view_requires_start_and_end(auth_client):
    response = auth_client.get(reverse('calendar-view'))
    assert response.status_code == 400


def test_calendar_view_returns_events_and_tasks_in_range(auth_client, user):
    from apps.calendar_events.models import Event
    from apps.tasks.models import Task

    today = timezone.localdate()
    start = _dt(0)
    Event.objects.create(
        user=user, title='In range', start_time=start, end_time=start + timezone.timedelta(hours=1)
    )
    Event.objects.create(
        user=user,
        title='Out of range',
        start_time=_dt(30),
        end_time=_dt(30) + timezone.timedelta(hours=1),
    )
    Task.objects.create(user=user, title='Due today', due_date=today)
    Task.objects.create(user=user, title='Due way later', due_date=today + dt.timedelta(days=30))

    response = auth_client.get(
        reverse('calendar-view'),
        {'start': str(today), 'end': str(today + dt.timedelta(days=1))},
    )

    assert response.status_code == 200
    body = response.json()
    assert [e['title'] for e in body['events']] == ['In range']
    assert [t['title'] for t in body['tasks']] == ['Due today']


def test_calendar_view_end_before_start_rejected(auth_client):
    today = timezone.localdate()
    response = auth_client.get(
        reverse('calendar-view'), {'start': str(today), 'end': str(today - dt.timedelta(days=1))}
    )
    assert response.status_code == 400


def test_daily_planner_returns_only_that_days_items(auth_client, user):
    from apps.calendar_events.models import Event
    from apps.tasks.models import Task

    today = timezone.localdate()
    Event.objects.create(
        user=user, title='Today event', start_time=_dt(0), end_time=_dt(0) + timezone.timedelta(hours=1)
    )
    Event.objects.create(
        user=user, title='Tomorrow event', start_time=_dt(1), end_time=_dt(1) + timezone.timedelta(hours=1)
    )
    Task.objects.create(user=user, title='Today task', due_date=today)

    response = auth_client.get(reverse('calendar-planner-daily'), {'date': str(today)})

    assert response.status_code == 200
    body = response.json()
    assert body['date'] == str(today)
    assert [e['title'] for e in body['events']] == ['Today event']
    assert [t['title'] for t in body['tasks']] == ['Today task']


def test_weekly_planner_breaks_down_by_day(auth_client, user):
    from apps.calendar_events.models import Event

    week_start = timezone.localdate()
    Event.objects.create(
        user=user, title='Day 0', start_time=_dt(0), end_time=_dt(0) + timezone.timedelta(hours=1)
    )
    Event.objects.create(
        user=user, title='Day 3', start_time=_dt(3), end_time=_dt(3) + timezone.timedelta(hours=1)
    )

    response = auth_client.get(reverse('calendar-planner-weekly'), {'start': str(week_start)})

    assert response.status_code == 200
    body = response.json()
    assert body['week_start'] == str(week_start)
    assert len(body['days']) == 7
    assert [e['title'] for e in body['days'][0]['events']] == ['Day 0']
    assert [e['title'] for e in body['days'][3]['events']] == ['Day 3']
    assert body['days'][1]['events'] == []
