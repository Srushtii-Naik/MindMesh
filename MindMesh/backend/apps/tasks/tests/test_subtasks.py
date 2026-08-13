import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_create_subtask(auth_client, task):
    response = auth_client.post(
        reverse('subtask-list', kwargs={'task_id': task.id}), {'title': 'Draft outline'}, format='json'
    )

    assert response.status_code == 201
    assert response.json()['title'] == 'Draft outline'
    assert response.json()['is_completed'] is False


def test_create_subtask_under_other_users_task_returns_404(auth_client, other_user):
    from apps.tasks.models import Task

    foreign_task = Task.objects.create(user=other_user, title='Not mine')

    response = auth_client.post(
        reverse('subtask-list', kwargs={'task_id': foreign_task.id}),
        {'title': 'Sneaky'},
        format='json',
    )
    assert response.status_code == 404


def test_list_subtasks(auth_client, task):
    from apps.tasks.models import SubTask

    SubTask.objects.create(task=task, title='One')
    SubTask.objects.create(task=task, title='Two')

    response = auth_client.get(reverse('subtask-list', kwargs={'task_id': task.id}))

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_update_subtask(auth_client, task):
    from apps.tasks.models import SubTask

    subtask = SubTask.objects.create(task=task, title='Draft')

    response = auth_client.patch(
        reverse('subtask-detail', kwargs={'task_id': task.id, 'subtask_id': subtask.id}),
        {'is_completed': True},
        format='json',
    )

    assert response.status_code == 200
    assert response.json()['is_completed'] is True


def test_delete_subtask_soft_deletes(auth_client, task):
    from apps.tasks.models import SubTask

    subtask = SubTask.objects.create(task=task, title='Draft')

    response = auth_client.delete(
        reverse('subtask-detail', kwargs={'task_id': task.id, 'subtask_id': subtask.id})
    )

    assert response.status_code == 204
    subtask.refresh_from_db()
    assert subtask.is_active is False

    list_response = auth_client.get(reverse('subtask-list', kwargs={'task_id': task.id}))
    assert list_response.json() == []


def test_task_detail_includes_subtasks(auth_client, task):
    from apps.tasks.models import SubTask

    SubTask.objects.create(task=task, title='Step one')

    response = auth_client.get(reverse('task-detail', kwargs={'task_id': task.id}))

    assert response.status_code == 200
    subtasks = response.json()['subtasks']
    assert len(subtasks) == 1
    assert subtasks[0]['title'] == 'Step one'
