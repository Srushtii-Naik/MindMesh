import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_create_note_requires_authentication(api_client):
    response = api_client.post(reverse('note-list'), {'title': 'Groceries'}, format='json')
    assert response.status_code == 401


def test_create_note(auth_client):
    response = auth_client.post(
        reverse('note-list'), {'title': 'Groceries', 'content': 'Milk, eggs, bread.'}, format='json'
    )

    assert response.status_code == 201
    body = response.json()
    assert body['title'] == 'Groceries'
    assert body['content'] == 'Milk, eggs, bread.'
    assert body['category'] is None
    assert body['tags'] == []
    assert body['attachments'] == []
    assert body['ai_summary'] == ''


def test_create_note_blank_title_rejected(auth_client):
    response = auth_client.post(reverse('note-list'), {'title': '   '}, format='json')
    assert response.status_code == 400


def test_create_note_with_category(auth_client, category):
    response = auth_client.post(
        reverse('note-list'),
        {'title': 'Groceries', 'category_id': str(category.id)},
        format='json',
    )

    assert response.status_code == 201
    assert response.json()['category']['id'] == str(category.id)


def test_create_note_with_other_users_category_is_rejected(auth_client, other_user):
    from apps.notes.models import Category

    foreign_category = Category.objects.create(user=other_user, name='Personal')

    response = auth_client.post(
        reverse('note-list'),
        {'title': 'Groceries', 'category_id': str(foreign_category.id)},
        format='json',
    )

    assert response.status_code == 404


def test_create_note_with_tags(auth_client, tag):
    response = auth_client.post(
        reverse('note-list'),
        {'title': 'Groceries', 'tag_ids': [str(tag.id)]},
        format='json',
    )

    assert response.status_code == 201
    tag_names = [item['name'] for item in response.json()['tags']]
    assert tag_names == ['urgent']


def test_create_note_with_unknown_tag_is_rejected(auth_client):
    import uuid

    response = auth_client.post(
        reverse('note-list'),
        {'title': 'Groceries', 'tag_ids': [str(uuid.uuid4())]},
        format='json',
    )

    assert response.status_code == 404


def test_list_notes_only_returns_own_notes(auth_client, user, other_user):
    from apps.notes.models import Note

    Note.objects.create(user=user, title='Mine')
    Note.objects.create(user=other_user, title='Not mine')

    response = auth_client.get(reverse('note-list'))

    assert response.status_code == 200
    titles = [item['title'] for item in response.json()['results']]
    assert titles == ['Mine']


def test_get_note_detail(auth_client, note):
    response = auth_client.get(reverse('note-detail', kwargs={'note_id': note.id}))
    assert response.status_code == 200
    assert response.json()['id'] == str(note.id)


def test_get_other_users_note_returns_404(auth_client, other_user):
    from apps.notes.models import Note

    foreign_note = Note.objects.create(user=other_user, title='Not mine')

    response = auth_client.get(reverse('note-detail', kwargs={'note_id': foreign_note.id}))
    assert response.status_code == 404


def test_update_note(auth_client, note):
    response = auth_client.patch(
        reverse('note-detail', kwargs={'note_id': note.id}),
        {'title': 'Updated title', 'content': 'Updated content.'},
        format='json',
    )

    assert response.status_code == 200
    body = response.json()
    assert body['title'] == 'Updated title'
    assert body['content'] == 'Updated content.'


def test_update_note_tags_replaces_existing_set(auth_client, note, tag, user):
    from apps.notes.models import Tag

    second_tag = Tag.objects.create(user=user, name='reference')
    note.tags.set([tag])

    response = auth_client.patch(
        reverse('note-detail', kwargs={'note_id': note.id}),
        {'tag_ids': [str(second_tag.id)]},
        format='json',
    )

    assert response.status_code == 200
    tag_names = [item['name'] for item in response.json()['tags']]
    assert tag_names == ['reference']


def test_update_note_can_clear_category(auth_client, note, category):
    note.category = category
    note.save()

    response = auth_client.patch(
        reverse('note-detail', kwargs={'note_id': note.id}),
        {'category_id': None},
        format='json',
    )

    assert response.status_code == 200
    assert response.json()['category'] is None


def test_delete_note_soft_deletes(auth_client, note):
    response = auth_client.delete(reverse('note-detail', kwargs={'note_id': note.id}))
    assert response.status_code == 204

    note.refresh_from_db()
    assert note.is_active is False
    assert note.deleted_at is not None

    get_response = auth_client.get(reverse('note-detail', kwargs={'note_id': note.id}))
    assert get_response.status_code == 404
