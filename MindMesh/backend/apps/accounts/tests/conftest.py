"""Shared fixtures for accounts app tests."""

import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def user(db) -> User:
    user = User.objects.create_user(
        email='jane@example.com', password='CorrectHorse123!', full_name='Jane Doe'
    )
    from apps.accounts.repositories import get_or_create_settings
    get_or_create_settings(user)
    return user


@pytest.fixture
def other_user(db) -> User:
    user = User.objects.create_user(
        email='john@example.com', password='CorrectHorse123!', full_name='John Roe'
    )
    from apps.accounts.repositories import get_or_create_settings
    get_or_create_settings(user)
    return user


@pytest.fixture
def auth_client(api_client, user) -> APIClient:
    """An APIClient with a valid access token for `user` already attached."""
    from apps.accounts.services import issue_tokens_for_user

    tokens = issue_tokens_for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
    return api_client
