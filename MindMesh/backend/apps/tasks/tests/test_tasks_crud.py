import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_create_task_requires_authentication(api_client):
    response = api_client.post(reverse('task-list'), {'title': 'Buy milk'}, format='json')
    assert response.status_code == 401


def test_create_task(auth_client):
    response = auth_client.post(reverse('task-list'), {'title': 'Buy milk'}, format='json')

    assert response.status_code == 201
    body = response.json()
    assert body['title'] == 'Buy milk'
    assert body['priority'] == 'medium'
    assert body['is_completed'] is False
    assert body['subtasks'] == []


def test_create_task_blank_title_rejected(auth_client):
    response = auth_client.post(reverse('task-list'), {'title': '   '}, format='json')
    assert response.status_code == 400


def test_create_task_with_category(auth_client, category):
    response = auth_client.post(
        reverse('task-list'),
        {'title': 'Buy milk', 'category_id': str(category.id)},
        format='json',
    )

    assert response.status_code == 201
    assert response.json()['category']['id'] == str(category.id)


def test_create_task_with_other_users_category_is_rejected(auth_client, other_user):
    from apps.tasks.models import Category

    foreign_category = Category.objects.create(user=other_user, name='Personal')

    response = auth_client.post(
        reverse('task-list'),
        {'title': 'Buy milk', 'category_id': str(foreign_category.id)},
        format='json',
    )

    assert response.status_code == 404


def test_list_tasks_only_returns_own_tasks(auth_client, user, other_user):
    from apps.tasks.models import Task

    Task.objects.create(user=user, title='Mine')
    Task.objects.create(user=other_user, title='Not mine')

    response = auth_client.get(reverse('task-list'))

    assert response.status_code == 200
    titles = [item['title'] for item in response.json()['results']]
    assert titles == ['Mine']


def test_get_task_detail(auth_client, task):
    response = auth_client.get(reverse('task-detail', kwargs={'task_id': task.id}))
    assert response.status_code == 200
    assert response.json()['id'] == str(task.id)


def test_get_other_users_task_returns_404(auth_client, other_user):
    from apps.tasks.models import Task

    foreign_task = Task.objects.create(user=other_user, title='Not mine')

    response = auth_client.get(reverse('task-detail', kwargs={'task_id': foreign_task.id}))
    assert response.status_code == 404


def test_update_task(auth_client, task):
    response = auth_client.patch(
        reverse('task-detail', kwargs={'task_id': task.id}),
        {'title': 'Updated title', 'priority': 'high'},
        format='json',
    )

    assert response.status_code == 200
    body = response.json()
    assert body['title'] == 'Updated title'
    assert body['priority'] == 'high'


def test_update_task_cannot_set_is_completed_directly(auth_client, task):
    """is_completed is intentionally not writable via PATCH — see TaskWriteSerializer."""
    response = auth_client.patch(
        reverse('task-detail', kwargs={'task_id': task.id}),
        {'is_completed': True},
        format='json',
    )

    assert response.status_code == 200
    assert response.json()['is_completed'] is False


def test_delete_task_soft_deletes(auth_client, task):
    response = auth_client.delete(reverse('task-detail', kwargs={'task_id': task.id}))
    assert response.status_code == 204

    task.refresh_from_db()
    assert task.is_active is False
    assert task.deleted_at is not None

    # No longer visible via the API.
    get_response = auth_client.get(reverse('task-detail', kwargs={'task_id': task.id}))
    assert get_response.status_code == 404


def test_complete_task(auth_client, task):
    response = auth_client.post(reverse('task-complete', kwargs={'task_id': task.id}))

    assert response.status_code == 200
    body = response.json()
    assert body['is_completed'] is True
    assert body['completed_at'] is not None


def test_reopen_task(auth_client, task):
    auth_client.post(reverse('task-complete', kwargs={'task_id': task.id}))

    response = auth_client.post(reverse('task-reopen', kwargs={'task_id': task.id}))

    assert response.status_code == 200
    body = response.json()
    assert body['is_completed'] is False
    assert body['completed_at'] is None
