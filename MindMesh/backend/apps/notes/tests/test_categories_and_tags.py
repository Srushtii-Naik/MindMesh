import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


# --------------------------------------------------------------------------
# Categories
# --------------------------------------------------------------------------


def test_create_category(auth_client):
    response = auth_client.post(reverse('note-category-list'), {'name': 'Ideas'}, format='json')
    assert response.status_code == 201
    assert response.json()['name'] == 'Ideas'


def test_create_duplicate_category_name_rejected(auth_client, category):
    response = auth_client.post(reverse('note-category-list'), {'name': 'Ideas'}, format='json')
    assert response.status_code == 409


def test_list_categories_only_returns_own(auth_client, category, other_user):
    from apps.notes.models import Category

    Category.objects.create(user=other_user, name='Not mine')

    response = auth_client.get(reverse('note-category-list'))

    assert response.status_code == 200
    names = [item['name'] for item in response.json()]
    assert names == ['Ideas']


def test_update_category(auth_client, category):
    response = auth_client.patch(
        reverse('note-category-detail', kwargs={'category_id': category.id}),
        {'name': 'Renamed'},
        format='json',
    )
    assert response.status_code == 200
    assert response.json()['name'] == 'Renamed'


def test_delete_category_nullifies_notes(auth_client, category, note):
    note.category = category
    note.save()

    response = auth_client.delete(
        reverse('note-category-detail', kwargs={'category_id': category.id})
    )
    assert response.status_code == 204

    note.refresh_from_db()
    assert note.category is None


def test_delete_other_users_category_returns_404(auth_client, other_user):
    from apps.notes.models import Category

    foreign_category = Category.objects.create(user=other_user, name='Not mine')

    response = auth_client.delete(
        reverse('note-category-detail', kwargs={'category_id': foreign_category.id})
    )
    assert response.status_code == 404


# --------------------------------------------------------------------------
# Tags
# --------------------------------------------------------------------------


def test_create_tag(auth_client):
    response = auth_client.post(reverse('note-tag-list'), {'name': 'urgent'}, format='json')
    assert response.status_code == 201
    assert response.json()['name'] == 'urgent'


def test_create_duplicate_tag_name_rejected(auth_client, tag):
    response = auth_client.post(reverse('note-tag-list'), {'name': 'urgent'}, format='json')
    assert response.status_code == 409


def test_delete_tag_removes_it_from_notes(auth_client, tag, note):
    note.tags.set([tag])

    response = auth_client.delete(reverse('note-tag-detail', kwargs={'tag_id': tag.id}))
    assert response.status_code == 204

    assert note.tags.count() == 0


# --------------------------------------------------------------------------
# Filtering & search
# --------------------------------------------------------------------------


def test_filter_notes_by_category(auth_client, user, category):
    from apps.notes.models import Note

    Note.objects.create(user=user, title='In category', category=category)
    Note.objects.create(user=user, title='No category')

    response = auth_client.get(reverse('note-list'), {'category_id': str(category.id)})

    titles = [item['title'] for item in response.json()['results']]
    assert titles == ['In category']


def test_filter_notes_by_tag(auth_client, user, tag):
    from apps.notes.models import Note

    tagged = Note.objects.create(user=user, title='Tagged')
    tagged.tags.set([tag])
    Note.objects.create(user=user, title='Untagged')

    response = auth_client.get(reverse('note-list'), {'tag_id': str(tag.id)})

    titles = [item['title'] for item in response.json()['results']]
    assert titles == ['Tagged']


def test_search_notes_matches_title_and_content(auth_client, user):
    from apps.notes.models import Note

    Note.objects.create(user=user, title='Doctor appointment', content='Bring insurance card.')
    Note.objects.create(user=user, title='Groceries', content='Remember to buy the doctor a gift.')
    Note.objects.create(user=user, title='Unrelated', content='Nothing relevant here.')

    response = auth_client.get(reverse('note-list'), {'search': 'doctor'})

    titles = sorted(item['title'] for item in response.json()['results'])
    assert titles == ['Doctor appointment', 'Groceries']
