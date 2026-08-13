import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def _create_task(user, **kwargs):
    from apps.tasks.models import Task

    defaults = {'title': 'Task', 'user': user}
    defaults.update(kwargs)
    return Task.objects.create(**defaults)


class TestTaskFiltering:
    def test_filter_by_priority(self, auth_client, user):
        _create_task(user, title='Low one', priority='low')
        _create_task(user, title='High one', priority='high')

        response = auth_client.get(reverse('task-list'), {'priority': 'high'})

        titles = [item['title'] for item in response.json()['results']]
        assert titles == ['High one']

    def test_filter_by_is_completed(self, auth_client, user):
        _create_task(user, title='Done', is_completed=True)
        _create_task(user, title='Not done', is_completed=False)

        response = auth_client.get(reverse('task-list'), {'is_completed': 'true'})

        titles = [item['title'] for item in response.json()['results']]
        assert titles == ['Done']

    def test_unfiltered_list_includes_both_completed_and_open_tasks(self, auth_client, user):
        """
        Regression test: DRF's BooleanField treats a missing query param as
        False (mirroring an unchecked HTML checkbox), which would silently
        filter every unfiltered list request down to open tasks only if
        is_completed were a BooleanField on TaskFilterSerializer. See that
        serializer's docstring.
        """
        _create_task(user, title='Done', is_completed=True)
        _create_task(user, title='Not done', is_completed=False)

        response = auth_client.get(reverse('task-list'))

        titles = {item['title'] for item in response.json()['results']}
        assert titles == {'Done', 'Not done'}

    def test_filter_by_category(self, auth_client, user, category):
        _create_task(user, title='Categorized', category=category)
        _create_task(user, title='Uncategorized')

        response = auth_client.get(reverse('task-list'), {'category_id': str(category.id)})

        titles = [item['title'] for item in response.json()['results']]
        assert titles == ['Categorized']

    def test_filter_by_due_date_range(self, auth_client, user):
        _create_task(user, title='Early', due_date='2026-01-01')
        _create_task(user, title='Late', due_date='2026-06-01')

        response = auth_client.get(
            reverse('task-list'), {'due_after': '2026-05-01', 'due_before': '2026-12-31'}
        )

        titles = [item['title'] for item in response.json()['results']]
        assert titles == ['Late']

    def test_search_by_title(self, auth_client, user):
        _create_task(user, title='Buy groceries')
        _create_task(user, title='Write report')

        response = auth_client.get(reverse('task-list'), {'search': 'report'})

        titles = [item['title'] for item in response.json()['results']]
        assert titles == ['Write report']

    def test_invalid_is_completed_value_rejected(self, auth_client):
        response = auth_client.get(reverse('task-list'), {'is_completed': 'maybe'})
        assert response.status_code == 400


class TestCategories:
    def test_create_category(self, auth_client):
        response = auth_client.post(
            reverse('task-category-list'), {'name': 'Work', 'color': '#ff0000'}, format='json'
        )

        assert response.status_code == 201
        assert response.json()['name'] == 'Work'

    def test_create_category_invalid_color_rejected(self, auth_client):
        response = auth_client.post(
            reverse('task-category-list'), {'name': 'Work', 'color': 'not-a-color'}, format='json'
        )
        assert response.status_code == 400

    def test_duplicate_category_name_rejected(self, auth_client, category):
        response = auth_client.post(
            reverse('task-category-list'), {'name': category.name}, format='json'
        )
        assert response.status_code == 409

    def test_list_categories_only_returns_own(self, auth_client, user, other_user):
        from apps.tasks.models import Category

        Category.objects.create(user=user, name='Mine')
        Category.objects.create(user=other_user, name='Not mine')

        response = auth_client.get(reverse('task-category-list'))

        names = [item['name'] for item in response.json()]
        assert names == ['Mine']

    def test_update_category(self, auth_client, category):
        response = auth_client.patch(
            reverse('task-category-detail', kwargs={'category_id': category.id}),
            {'name': 'Renamed'},
            format='json',
        )
        assert response.status_code == 200
        assert response.json()['name'] == 'Renamed'

    def test_delete_category_detaches_tasks_rather_than_deleting_them(
        self, auth_client, user, category
    ):
        task = _create_task(user, category=category)

        response = auth_client.delete(
            reverse('task-category-detail', kwargs={'category_id': category.id})
        )
        assert response.status_code == 204

        task.refresh_from_db()
        assert task.category_id is None

    def test_other_users_category_returns_404(self, auth_client, other_user):
        from apps.tasks.models import Category

        foreign = Category.objects.create(user=other_user, name='Not mine')

        response = auth_client.get(
            reverse('task-category-detail', kwargs={'category_id': foreign.id})
        )
        assert response.status_code == 404
