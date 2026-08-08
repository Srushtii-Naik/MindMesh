"""
Regression tests for the existing core authentication flow (Milestone 2.1).

Not rewritten as part of Milestone 2 remaining scope — these exist to prove
the new work (Google OAuth, password reset, profile, settings, sessions)
did not regress the working core system.
"""

import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_register_creates_user_and_returns_tokens(api_client):
    response = api_client.post(
        reverse('auth-register'),
        {
            'email': 'new@example.com',
            'full_name': 'New User',
            'password': 'Str0ng!Passw0rd',
            'password_confirm': 'Str0ng!Passw0rd',
        },
        format='json',
    )

    assert response.status_code == 201
    assert response.data['user']['email'] == 'new@example.com'
    assert 'access' in response.data
    assert 'refresh' in response.data


def test_register_duplicate_email_returns_409(api_client, user):
    response = api_client.post(
        reverse('auth-register'),
        {
            'email': user.email,
            'full_name': 'Someone Else',
            'password': 'Str0ng!Passw0rd',
            'password_confirm': 'Str0ng!Passw0rd',
        },
        format='json',
    )

    assert response.status_code == 409
    assert response.data['code'] == 'email_already_registered'


def test_register_mismatched_passwords_returns_400(api_client):
    response = api_client.post(
        reverse('auth-register'),
        {
            'email': 'mismatch@example.com',
            'full_name': 'Mismatch User',
            'password': 'Str0ng!Passw0rd',
            'password_confirm': 'Different!Passw0rd',
        },
        format='json',
    )

    assert response.status_code == 400


def test_login_with_correct_credentials_returns_tokens(api_client, user):
    response = api_client.post(
        reverse('auth-login'),
        {'email': user.email, 'password': 'CorrectHorse123!'},
        format='json',
    )

    assert response.status_code == 200
    assert response.data['user']['email'] == user.email
    assert 'access' in response.data
    assert 'refresh' in response.data


def test_login_with_wrong_password_returns_401(api_client, user):
    response = api_client.post(
        reverse('auth-login'),
        {'email': user.email, 'password': 'WrongPassword!'},
        format='json',
    )

    assert response.status_code == 401


def test_logout_blacklists_refresh_token(api_client, user):
    login_response = api_client.post(
        reverse('auth-login'),
        {'email': user.email, 'password': 'CorrectHorse123!'},
        format='json',
    )
    access, refresh = login_response.data['access'], login_response.data['refresh']

    logout_response = api_client.post(
        reverse('auth-logout'),
        {'refresh': refresh},
        format='json',
        HTTP_AUTHORIZATION=f'Bearer {access}',
    )
    assert logout_response.status_code == 204

    refresh_response = api_client.post(
        reverse('auth-token-refresh'), {'refresh': refresh}, format='json'
    )
    assert refresh_response.status_code == 401


def test_logout_requires_authentication(api_client, user):
    response = api_client.post(reverse('auth-logout'), {'refresh': 'irrelevant'}, format='json')
    assert response.status_code == 401


def test_health_check_remains_public(api_client):
    response = api_client.get('/api/v1/health/')
    assert response.status_code == 200
    assert response.data == {'status': 'ok'}
