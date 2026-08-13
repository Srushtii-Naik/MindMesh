"""Shared fixtures for tasks app tests."""

import pytest

from apps.tasks.models import Category, Task


@pytest.fixture
def category(user) -> Category:
    return Category.objects.create(user=user, name='Work', color='#5f6dfa')


@pytest.fixture
def task(user) -> Task:
    return Task.objects.create(user=user, title='Write project report')
