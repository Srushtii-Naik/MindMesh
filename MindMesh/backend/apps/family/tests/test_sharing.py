import pytest
from django.urls import reverse
from django.utils import timezone

pytestmark = pytest.mark.django_db


@pytest.fixture
def family_with_two_members(family_with_owner, other_user):
    """`user` (owner) + `other_user` (adult) in the same family."""
    from apps.family.models import FamilyRole
    from apps.family.repositories import create_membership

    create_membership(family=family_with_owner, user=other_user, role=FamilyRole.ADULT)
    return family_with_owner


@pytest.fixture
def owned_task(user):
    from apps.tasks.models import Task

    return Task.objects.create(user=user, title='Take out the trash')


@pytest.fixture
def owned_event(user):
    from apps.calendar_events.models import Event

    now = timezone.now()
    return Event.objects.create(
        user=user, title='Dentist', start_time=now, end_time=now + timezone.timedelta(hours=1)
    )


@pytest.fixture
def owned_note(user):
    from apps.notes.models import Note

    return Note.objects.create(user=user, title='Grocery list', content='Milk, eggs')


# --------------------------------------------------------------------------
# Shared tasks
# --------------------------------------------------------------------------


def test_share_task_with_family(family_with_two_members, auth_client, owned_task):
    response = auth_client.post(
        reverse('shared-task-list-create', args=[family_with_two_members.id]),
        {'resource_id': str(owned_task.id), 'can_edit': True},
        format='json',
    )
    assert response.status_code == 201
    assert response.json()['can_edit'] is True


def test_family_member_sees_shared_task(
    family_with_two_members, auth_client, other_client, owned_task
):
    auth_client.post(
        reverse('shared-task-list-create', args=[family_with_two_members.id]),
        {'resource_id': str(owned_task.id)},
        format='json',
    )

    response = other_client.get(
        reverse('shared-task-list-create', args=[family_with_two_members.id])
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]['task']['id'] == str(owned_task.id)


def test_non_owner_cannot_share_someone_elses_task(
    family_with_two_members, other_client, owned_task
):
    """other_user is a family member but doesn't own owned_task."""
    response = other_client.post(
        reverse('shared-task-list-create', args=[family_with_two_members.id]),
        {'resource_id': str(owned_task.id)},
        format='json',
    )
    assert response.status_code == 404
    assert response.json()['code'] == 'resource_not_found'


def test_cannot_share_task_twice(family_with_two_members, auth_client, owned_task):
    url = reverse('shared-task-list-create', args=[family_with_two_members.id])
    auth_client.post(url, {'resource_id': str(owned_task.id)}, format='json')
    response = auth_client.post(url, {'resource_id': str(owned_task.id)}, format='json')

    assert response.status_code == 409
    assert response.json()['code'] == 'resource_already_shared'


def test_view_only_share_blocks_edit(
    family_with_two_members, auth_client, other_client, owned_task
):
    shared = auth_client.post(
        reverse('shared-task-list-create', args=[family_with_two_members.id]),
        {'resource_id': str(owned_task.id), 'can_edit': False},
        format='json',
    ).json()

    response = other_client.patch(
        reverse('shared-task-edit', args=[family_with_two_members.id, shared['id']]),
        {'title': 'Hijacked title'},
        format='json',
    )
    assert response.status_code == 403
    assert response.json()['code'] == 'share_permission_denied'


def test_can_edit_share_allows_delegated_task_edit(
    family_with_two_members, auth_client, other_client, owned_task
):
    """PRD.md Section 6.4: 'delegate tasks to my children' — a member with
    edit access can update and complete a shared task on the owner's behalf."""
    shared = auth_client.post(
        reverse('shared-task-list-create', args=[family_with_two_members.id]),
        {'resource_id': str(owned_task.id), 'can_edit': True},
        format='json',
    ).json()

    edit = other_client.patch(
        reverse('shared-task-edit', args=[family_with_two_members.id, shared['id']]),
        {'title': 'Take out the trash tonight'},
        format='json',
    )
    assert edit.status_code == 200
    assert edit.json()['title'] == 'Take out the trash tonight'

    complete = other_client.post(
        reverse('shared-task-complete', args=[family_with_two_members.id, shared['id']])
    )
    assert complete.status_code == 200
    assert complete.json()['is_completed'] is True

    owned_task.refresh_from_db()
    assert owned_task.is_completed is True


def test_only_owner_or_family_owner_can_unshare(
    family_with_two_members, third_user, third_client, other_client, auth_client, owned_task,
):
    from apps.family.models import FamilyRole
    from apps.family.repositories import create_membership

    create_membership(family=family_with_two_members, user=third_user, role=FamilyRole.ADULT)

    shared = auth_client.post(
        reverse('shared-task-list-create', args=[family_with_two_members.id]),
        {'resource_id': str(owned_task.id)},
        format='json',
    ).json()

    # third_user is neither the resource owner nor the family owner.
    forbidden = third_client.delete(
        reverse('shared-task-detail', args=[family_with_two_members.id, shared['id']])
    )
    assert forbidden.status_code == 403
    assert forbidden.json()['code'] == 'share_permission_denied'

    allowed = auth_client.delete(
        reverse('shared-task-detail', args=[family_with_two_members.id, shared['id']])
    )
    assert allowed.status_code == 204

    listing = other_client.get(
        reverse('shared-task-list-create', args=[family_with_two_members.id])
    )
    assert listing.json() == []


def test_deleting_source_task_removes_it_from_shared_listing(
    family_with_two_members, auth_client, other_client, owned_task,
):
    auth_client.post(
        reverse('shared-task-list-create', args=[family_with_two_members.id]),
        {'resource_id': str(owned_task.id)},
        format='json',
    )

    # Soft-delete the underlying task directly (owner is `user`).
    owned_task.is_active = False
    owned_task.deleted_at = timezone.now()
    owned_task.save(update_fields=['is_active', 'deleted_at'])

    response = other_client.get(
        reverse('shared-task-list-create', args=[family_with_two_members.id])
    )
    assert response.status_code == 200
    assert response.json() == []


# --------------------------------------------------------------------------
# Shared events & notes (view-only this milestone)
# --------------------------------------------------------------------------


def test_share_event_with_family(family_with_two_members, auth_client, other_client, owned_event):
    share = auth_client.post(
        reverse('shared-event-list-create', args=[family_with_two_members.id]),
        {'resource_id': str(owned_event.id)},
        format='json',
    )
    assert share.status_code == 201

    listing = other_client.get(
        reverse('shared-event-list-create', args=[family_with_two_members.id])
    )
    assert listing.status_code == 200
    assert listing.json()[0]['event']['id'] == str(owned_event.id)


def test_share_note_with_family(family_with_two_members, auth_client, other_client, owned_note):
    share = auth_client.post(
        reverse('shared-note-list-create', args=[family_with_two_members.id]),
        {'resource_id': str(owned_note.id)},
        format='json',
    )
    assert share.status_code == 201

    listing = other_client.get(
        reverse('shared-note-list-create', args=[family_with_two_members.id])
    )
    assert listing.status_code == 200
    assert listing.json()[0]['note']['id'] == str(owned_note.id)


def test_non_member_cannot_list_shared_tasks(family_with_two_members, third_client):
    response = third_client.get(
        reverse('shared-task-list-create', args=[family_with_two_members.id])
    )
    assert response.status_code == 403
    assert response.json()['code'] == 'not_family_member'
