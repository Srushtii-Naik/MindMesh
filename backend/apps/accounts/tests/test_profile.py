"""Tests for the user profile endpoints (GET/PATCH /api/v1/auth/me/)."""

import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_get_profile_requires_authentication(api_client):
    response = api_client.get(reverse('auth-profile'))
    assert response.status_code == 401


def test_get_profile_returns_current_user(auth_client, user):
    response = auth_client.get(reverse('auth-profile'))

    assert response.status_code == 200
    assert response.data['email'] == user.email
    assert response.data['full_name'] == user.full_name
    assert response.data['auth_provider'] == 'email'


def test_patch_profile_updates_full_name(auth_client, user):
    response = auth_client.patch(reverse('auth-profile'), {'full_name': 'Jane Updated'}, format='json')

    assert response.status_code == 200
    assert response.data['full_name'] == 'Jane Updated'

    user.refresh_from_db()
    assert user.full_name == 'Jane Updated'


def test_patch_profile_rejects_blank_full_name(auth_client):
    response = auth_client.patch(reverse('auth-profile'), {'full_name': '   '}, format='json')
    assert response.status_code == 400


def test_patch_profile_does_not_allow_email_change(auth_client, user):
    response = auth_client.patch(
        reverse('auth-profile'),
        {'full_name': 'Jane Doe', 'email': 'hijacked@example.com'},
        format='json',
    )

    assert response.status_code == 200
    user.refresh_from_db()
    assert user.email == 'jane@example.com'


def test_profile_is_scoped_to_the_authenticated_user(auth_client, other_user):
    response = auth_client.get(reverse('auth-profile'))
    assert response.data['email'] != other_user.email
