"""Tests for account settings endpoints (GET/PATCH /api/v1/auth/settings/)."""

import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_get_settings_requires_authentication(api_client):
    response = api_client.get(reverse('auth-settings'))
    assert response.status_code == 401


def test_get_settings_returns_defaults(auth_client):
    response = auth_client.get(reverse('auth-settings'))

    assert response.status_code == 200
    assert response.data['theme_preference'] == 'system'
    assert response.data['email_notifications_enabled'] is True


def test_patch_settings_updates_theme(auth_client, user):
    response = auth_client.patch(
        reverse('auth-settings'), {'theme_preference': 'dark'}, format='json'
    )

    assert response.status_code == 200
    assert response.data['theme_preference'] == 'dark'

    user.settings.refresh_from_db()
    assert user.settings.theme_preference == 'dark'


def test_patch_settings_updates_notifications_flag(auth_client):
    response = auth_client.patch(
        reverse('auth-settings'), {'email_notifications_enabled': False}, format='json'
    )

    assert response.status_code == 200
    assert response.data['email_notifications_enabled'] is False


def test_patch_settings_rejects_invalid_theme(auth_client):
    response = auth_client.patch(
        reverse('auth-settings'), {'theme_preference': 'neon'}, format='json'
    )
    assert response.status_code == 400


def test_settings_are_scoped_per_user(auth_client, other_user):
    auth_client.patch(reverse('auth-settings'), {'theme_preference': 'dark'}, format='json')

    other_user.settings.refresh_from_db()
    assert other_user.settings.theme_preference == 'system'
