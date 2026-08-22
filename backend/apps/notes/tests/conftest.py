"""Shared fixtures for notes app tests."""

import pytest

from apps.notes.models import Category, Note, Tag


@pytest.fixture
def category(user) -> Category:
    return Category.objects.create(user=user, name='Ideas', color='#5f6dfa')


@pytest.fixture
def tag(user) -> Tag:
    return Tag.objects.create(user=user, name='urgent')


@pytest.fixture
def note(user) -> Note:
    return Note.objects.create(user=user, title='Doctor visit', content='Book a follow-up appointment.')
