"""
Regression tests for the existing core authentication flow (Milestone 2.1).

Not rewritten as part of Milestone 2 remaining scope — these exist to prove
the new work (Google OAuth, password reset, profile, settings, sessions)
did not regress the working core system.

Milestone 12 note: the refresh token moved from the JSON response body to an
httpOnly cookie (ADR 0001). The assertions below were updated accordingly;
see test_cookie_auth.py for dedicated coverage of the cookie/CSRF mechanism
itself.
"""

from django.conf import settings

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
    # Refresh token is delivered via httpOnly cookie, not the JSON body.
    assert 'refresh' not in response.data
    assert settings.AUTH_REFRESH_COOKIE_NAME in response.cookies
    assert response.cookies[settings.AUTH_REFRESH_COOKIE_NAME]['httponly'] is True


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
    assert 'refresh' not in response.data
    assert settings.AUTH_REFRESH_COOKIE_NAME in response.cookies
    assert settings.AUTH_CSRF_COOKIE_NAME in response.cookies
    # The CSRF cookie must be JS-readable so the frontend can echo it back
    # as a header on refresh/logout — it must NOT be httponly.
    assert response.cookies[settings.AUTH_CSRF_COOKIE_NAME]['httponly'] == ''


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
    access = login_response.data['access']
    csrf_token = login_response.cookies[settings.AUTH_CSRF_COOKIE_NAME].value

    # api_client is a single test-client instance, so the refresh/CSRF
    # cookies set by login above are automatically resent on the requests
    # below — only the CSRF header must be attached explicitly, mirroring
    # what the frontend Axios client does (reads the readable cookie value,
    # sends it as a header; the browser handles the cookie itself).
    logout_response = api_client.post(
        reverse('auth-logout'),
        format='json',
        HTTP_AUTHORIZATION=f'Bearer {access}',
        HTTP_X_CSRF_TOKEN=csrf_token,
    )
    assert logout_response.status_code == 204
    assert settings.AUTH_REFRESH_COOKIE_NAME not in api_client.cookies or (
        api_client.cookies[settings.AUTH_REFRESH_COOKIE_NAME].value == ''
    )

    refresh_response = api_client.post(
        reverse('auth-token-refresh'), format='json', HTTP_X_CSRF_TOKEN=csrf_token
    )
    assert refresh_response.status_code in (401, 403)


def test_logout_requires_authentication(api_client, user):
    response = api_client.post(reverse('auth-logout'), {'refresh': 'irrelevant'}, format='json')
    assert response.status_code == 401


def test_health_check_remains_public(api_client):
    response = api_client.get('/api/v1/health/')
    assert response.status_code == 200
    assert response.data == {'status': 'ok'}
