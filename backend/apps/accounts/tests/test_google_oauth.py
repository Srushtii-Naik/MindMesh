"""Tests for Google OAuth sign-in (POST /api/v1/auth/google/)."""

from unittest.mock import patch

import pytest
from django.urls import reverse

from apps.accounts.models import AuthProvider, User

pytestmark = pytest.mark.django_db


def _google_claims(**overrides) -> dict:
    claims = {
        'sub': 'google-subject-123',
        'email': 'newgoogleuser@example.com',
        'email_verified': True,
        'name': 'Google User',
    }
    claims.update(overrides)
    return claims


@patch('apps.accounts.services.google_id_token.verify_oauth2_token')
def test_google_login_creates_new_user(mock_verify, api_client):
    mock_verify.return_value = _google_claims()

    response = api_client.post(reverse('auth-google'), {'id_token': 'fake-token'}, format='json')

    assert response.status_code == 200
    assert response.data['user']['email'] == 'newgoogleuser@example.com'
    assert 'access' in response.data
    assert 'refresh' not in response.data

    created = User.objects.get(email='newgoogleuser@example.com')
    assert created.auth_provider == AuthProvider.GOOGLE
    assert created.google_sub == 'google-subject-123'
    assert created.has_usable_password() is False


@patch('apps.accounts.services.google_id_token.verify_oauth2_token')
def test_google_login_returns_existing_user_on_repeat_login(mock_verify, api_client):
    mock_verify.return_value = _google_claims()

    first = api_client.post(reverse('auth-google'), {'id_token': 'fake-token'}, format='json')
    second = api_client.post(reverse('auth-google'), {'id_token': 'fake-token'}, format='json')

    assert first.data['user']['id'] == second.data['user']['id']
    assert User.objects.filter(google_sub='google-subject-123').count() == 1


@patch('apps.accounts.services.google_id_token.verify_oauth2_token')
def test_google_login_rejects_unverified_email(mock_verify, api_client):
    mock_verify.return_value = _google_claims(email_verified=False)

    response = api_client.post(reverse('auth-google'), {'id_token': 'fake-token'}, format='json')

    assert response.status_code == 401
    assert response.data['code'] == 'invalid_google_token'


@patch('apps.accounts.services.google_id_token.verify_oauth2_token')
def test_google_login_rejects_invalid_token(mock_verify, api_client):
    mock_verify.side_effect = ValueError('Token expired')

    response = api_client.post(reverse('auth-google'), {'id_token': 'garbage'}, format='json')

    assert response.status_code == 401
    assert response.data['code'] == 'invalid_google_token'


@patch('apps.accounts.services.google_id_token.verify_oauth2_token')
def test_google_login_conflicts_with_existing_email_password_account(mock_verify, api_client, user):
    mock_verify.return_value = _google_claims(email=user.email, sub='some-other-google-sub')

    response = api_client.post(reverse('auth-google'), {'id_token': 'fake-token'}, format='json')

    assert response.status_code == 409
    assert response.data['code'] == 'email_already_registered'


def test_google_login_requires_id_token_field(api_client):
    response = api_client.post(reverse('auth-google'), {}, format='json')
    assert response.status_code == 400
