import pytest
from django.urls import reverse
from django.utils import timezone

pytestmark = pytest.mark.django_db


def _iso(dt):
    return dt.isoformat()


def test_create_event_requires_authentication(api_client):
    response = api_client.post(reverse('calendar-event-list'), {'title': 'Standup'}, format='json')
    assert response.status_code == 401


def test_create_event(auth_client):
    start = timezone.now()
    end = start + timezone.timedelta(hours=1)

    response = auth_client.post(
        reverse('calendar-event-list'),
        {'title': 'Team sync', 'start_time': _iso(start), 'end_time': _iso(end)},
        format='json',
    )

    assert response.status_code == 201
    body = response.json()
    assert body['title'] == 'Team sync'
    assert body['all_day'] is False
    assert body['task'] is None


def test_create_event_blank_title_rejected(auth_client):
    start = timezone.now()
    end = start + timezone.timedelta(hours=1)

    response = auth_client.post(
        reverse('calendar-event-list'),
        {'title': '   ', 'start_time': _iso(start), 'end_time': _iso(end)},
        format='json',
    )
    assert response.status_code == 400


def test_create_event_missing_required_fields_rejected(auth_client):
    response = auth_client.post(reverse('calendar-event-list'), {}, format='json')
    assert response.status_code == 400


def test_create_event_end_before_start_rejected(auth_client):
    start = timezone.now()
    end = start - timezone.timedelta(hours=1)

    response = auth_client.post(
        reverse('calendar-event-list'),
        {'title': 'Bad range', 'start_time': _iso(start), 'end_time': _iso(end)},
        format='json',
    )

    assert response.status_code == 400
    assert response.json()['code'] == 'invalid_event_range'


def test_create_event_with_task_link(auth_client, task_for_event):
    start = timezone.now()
    end = start + timezone.timedelta(hours=1)

    response = auth_client.post(
        reverse('calendar-event-list'),
        {
            'title': 'Report review',
            'start_time': _iso(start),
            'end_time': _iso(end),
            'task_id': str(task_for_event.id),
        },
        format='json',
    )

    assert response.status_code == 201
    assert response.json()['task']['id'] == str(task_for_event.id)


def test_create_event_with_other_users_task_is_rejected(auth_client, other_user):
    from apps.tasks.models import Task

    foreign_task = Task.objects.create(user=other_user, title='Not mine')
    start = timezone.now()
    end = start + timezone.timedelta(hours=1)

    response = auth_client.post(
        reverse('calendar-event-list'),
        {
            'title': 'Report review',
            'start_time': _iso(start),
            'end_time': _iso(end),
            'task_id': str(foreign_task.id),
        },
        format='json',
    )

    assert response.status_code == 404
    assert response.json()['code'] == 'task_not_found'


def test_list_events_only_returns_own_events(auth_client, user, other_user):
    from apps.calendar_events.models import Event

    start = timezone.now()
    end = start + timezone.timedelta(hours=1)
    Event.objects.create(user=user, title='Mine', start_time=start, end_time=end)
    Event.objects.create(user=other_user, title='Not mine', start_time=start, end_time=end)

    response = auth_client.get(reverse('calendar-event-list'))

    assert response.status_code == 200
    titles = [item['title'] for item in response.json()['results']]
    assert titles == ['Mine']


def test_get_event_detail(auth_client, event):
    response = auth_client.get(reverse('calendar-event-detail', kwargs={'event_id': event.id}))
    assert response.status_code == 200
    assert response.json()['id'] == str(event.id)


def test_get_other_users_event_returns_404(auth_client, other_user):
    from apps.calendar_events.models import Event

    start = timezone.now()
    foreign_event = Event.objects.create(
        user=other_user, title='Not mine', start_time=start, end_time=start + timezone.timedelta(hours=1)
    )

    response = auth_client.get(reverse('calendar-event-detail', kwargs={'event_id': foreign_event.id}))
    assert response.status_code == 404


def test_update_event(auth_client, event):
    response = auth_client.patch(
        reverse('calendar-event-detail', kwargs={'event_id': event.id}),
        {'title': 'Updated title'},
        format='json',
    )
    assert response.status_code == 200
    assert response.json()['title'] == 'Updated title'


def test_update_event_invalid_range_rejected(auth_client, event):
    response = auth_client.patch(
        reverse('calendar-event-detail', kwargs={'event_id': event.id}),
        {'end_time': _iso(event.start_time - timezone.timedelta(hours=2))},
        format='json',
    )
    assert response.status_code == 400
    assert response.json()['code'] == 'invalid_event_range'


def test_delete_event_soft_deletes(auth_client, event):
    response = auth_client.delete(reverse('calendar-event-detail', kwargs={'event_id': event.id}))
    assert response.status_code == 204

    event.refresh_from_db()
    assert event.is_active is False
    assert event.deleted_at is not None

    response = auth_client.get(reverse('calendar-event-detail', kwargs={'event_id': event.id}))
    assert response.status_code == 404


def test_filter_events_by_task_id(auth_client, task_for_event):
    from apps.calendar_events.models import Event

    start = timezone.now()
    end = start + timezone.timedelta(hours=1)
    linked = Event.objects.create(
        user=task_for_event.user, title='Linked', start_time=start, end_time=end, task=task_for_event
    )
    Event.objects.create(user=task_for_event.user, title='Unlinked', start_time=start, end_time=end)

    response = auth_client.get(reverse('calendar-event-list'), {'task_id': str(task_for_event.id)})

    assert response.status_code == 200
    ids = [item['id'] for item in response.json()['results']]
    assert ids == [str(linked.id)]
