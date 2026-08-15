import pytest
from django.urls import reverse
from django.utils import timezone

pytestmark = pytest.mark.django_db


def _iso(dt):
    return dt.isoformat()


def test_create_reminder_requires_authentication(api_client):
    response = api_client.post(reverse('reminder-list'), {'title': 'Water plants'}, format='json')
    assert response.status_code == 401


def test_create_reminder(auth_client):
    remind_at = timezone.now() + timezone.timedelta(hours=1)

    response = auth_client.post(
        reverse('reminder-list'),
        {'title': 'Water plants', 'remind_at': _iso(remind_at)},
        format='json',
    )

    assert response.status_code == 201
    body = response.json()
    assert body['title'] == 'Water plants'
    assert body['is_sent'] is False
    assert body['trigger_type'] == 'time'
    assert body['task'] is None
    assert body['event'] is None


def test_create_reminder_blank_title_rejected(auth_client):
    remind_at = timezone.now() + timezone.timedelta(hours=1)
    response = auth_client.post(
        reverse('reminder-list'), {'title': '  ', 'remind_at': _iso(remind_at)}, format='json'
    )
    assert response.status_code == 400


def test_create_reminder_missing_fields_rejected(auth_client):
    response = auth_client.post(reverse('reminder-list'), {}, format='json')
    assert response.status_code == 400


def test_create_reminder_with_task_link(auth_client, user):
    from apps.tasks.models import Task

    task = Task.objects.create(user=user, title='Submit report')
    remind_at = timezone.now() + timezone.timedelta(hours=1)

    response = auth_client.post(
        reverse('reminder-list'),
        {'title': 'Reminder for report', 'remind_at': _iso(remind_at), 'task_id': str(task.id)},
        format='json',
    )

    assert response.status_code == 201
    assert response.json()['task']['id'] == str(task.id)


def test_create_reminder_with_other_users_task_rejected(auth_client, other_user):
    from apps.tasks.models import Task

    foreign_task = Task.objects.create(user=other_user, title='Not mine')
    remind_at = timezone.now() + timezone.timedelta(hours=1)

    response = auth_client.post(
        reverse('reminder-list'),
        {'title': 'Bad link', 'remind_at': _iso(remind_at), 'task_id': str(foreign_task.id)},
        format='json',
    )

    assert response.status_code == 404
    assert response.json()['code'] == 'task_not_found'


def test_create_reminder_with_event_link(auth_client, user):
    from apps.calendar_events.models import Event

    start = timezone.now() + timezone.timedelta(days=1)
    event = Event.objects.create(
        user=user, title='Appointment', start_time=start, end_time=start + timezone.timedelta(hours=1)
    )
    remind_at = start - timezone.timedelta(hours=1)

    response = auth_client.post(
        reverse('reminder-list'),
        {'title': 'Appointment reminder', 'remind_at': _iso(remind_at), 'event_id': str(event.id)},
        format='json',
    )

    assert response.status_code == 201
    assert response.json()['event']['id'] == str(event.id)


def test_create_reminder_with_other_users_event_rejected(auth_client, other_user):
    from apps.calendar_events.models import Event

    start = timezone.now() + timezone.timedelta(days=1)
    foreign_event = Event.objects.create(
        user=other_user, title='Not mine', start_time=start, end_time=start + timezone.timedelta(hours=1)
    )
    remind_at = timezone.now() + timezone.timedelta(hours=1)

    response = auth_client.post(
        reverse('reminder-list'),
        {'title': 'Bad link', 'remind_at': _iso(remind_at), 'event_id': str(foreign_event.id)},
        format='json',
    )

    assert response.status_code == 404
    assert response.json()['code'] == 'event_not_found'


def test_list_reminders_only_returns_own(auth_client, user, other_user):
    from apps.reminders.models import Reminder

    remind_at = timezone.now() + timezone.timedelta(hours=1)
    Reminder.objects.create(user=user, title='Mine', remind_at=remind_at)
    Reminder.objects.create(user=other_user, title='Not mine', remind_at=remind_at)

    response = auth_client.get(reverse('reminder-list'))

    assert response.status_code == 200
    titles = [item['title'] for item in response.json()['results']]
    assert titles == ['Mine']


def test_get_reminder_detail(auth_client, reminder):
    response = auth_client.get(reverse('reminder-detail', kwargs={'reminder_id': reminder.id}))
    assert response.status_code == 200
    assert response.json()['id'] == str(reminder.id)


def test_get_other_users_reminder_returns_404(auth_client, other_user):
    from apps.reminders.models import Reminder

    remind_at = timezone.now() + timezone.timedelta(hours=1)
    foreign_reminder = Reminder.objects.create(user=other_user, title='Not mine', remind_at=remind_at)

    response = auth_client.get(
        reverse('reminder-detail', kwargs={'reminder_id': foreign_reminder.id})
    )
    assert response.status_code == 404


def test_update_reminder(auth_client, reminder):
    response = auth_client.patch(
        reverse('reminder-detail', kwargs={'reminder_id': reminder.id}),
        {'title': 'Updated title'},
        format='json',
    )
    assert response.status_code == 200
    assert response.json()['title'] == 'Updated title'


def test_delete_reminder_soft_deletes(auth_client, reminder):
    response = auth_client.delete(reverse('reminder-detail', kwargs={'reminder_id': reminder.id}))
    assert response.status_code == 204

    reminder.refresh_from_db()
    assert reminder.is_active is False
    assert reminder.deleted_at is not None

    response = auth_client.get(reverse('reminder-detail', kwargs={'reminder_id': reminder.id}))
    assert response.status_code == 404


def test_filter_reminders_by_is_sent(auth_client, user):
    from apps.reminders.models import Reminder

    remind_at = timezone.now() + timezone.timedelta(hours=1)
    Reminder.objects.create(user=user, title='Pending', remind_at=remind_at, is_sent=False)
    Reminder.objects.create(user=user, title='Sent', remind_at=remind_at, is_sent=True)

    response = auth_client.get(reverse('reminder-list'), {'is_sent': 'false'})

    assert response.status_code == 200
    titles = [item['title'] for item in response.json()['results']]
    assert titles == ['Pending']
