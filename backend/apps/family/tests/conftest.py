"""Shared fixtures for family app tests."""

import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.accounts.services import issue_tokens_for_user
from apps.family.models import Family, FamilyMembership, FamilyRole
from apps.family.repositories import create_membership


@pytest.fixture
def third_user(db) -> User:
    u = User.objects.create_user(
        email='alex@example.com', password='CorrectHorse123!', full_name='Alex Kim'
    )
    from apps.accounts.repositories import get_or_create_settings

    get_or_create_settings(u)
    return u


def client_for(user: User) -> APIClient:
    """Builds an authenticated APIClient for an arbitrary user (mirrors
    conftest.py's `auth_client`, generalized for multi-user family tests)."""
    client = APIClient()
    tokens = issue_tokens_for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
    return client


@pytest.fixture
def other_client(other_user) -> APIClient:
    return client_for(other_user)


@pytest.fixture
def third_client(third_user) -> APIClient:
    return client_for(third_user)


@pytest.fixture
def family(user) -> Family:
    """A family owned by `user`."""
    return Family.objects.create(name='The Does', created_by=user)


@pytest.fixture
def owner_membership(family, user) -> FamilyMembership:
    return create_membership(family=family, user=user, role=FamilyRole.OWNER)


@pytest.fixture
def family_with_owner(family, owner_membership) -> Family:
    """A family that already has `user` as its OWNER member."""
    return family
