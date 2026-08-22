"""
Tests for the httpOnly refresh-token cookie and double-submit CSRF
mechanism introduced in Milestone 12 to resolve ADR 0001
(docs/adr/0001-token-storage-strategy.md).

test_registration_and_login.py and test_google_oauth.py already assert the
basic shape (refresh absent from JSON, present as a cookie); this file
covers the refresh/logout round trip and the CSRF failure modes.
"""

from django.conf import settings

import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def _login(api_client, user):
    return api_client.post(
        reverse('auth-login'),
        {'email': user.email, 'password': 'CorrectHorse123!'},
        format='json',
    )


def test_refresh_cookie_is_httponly_secure_and_samesite_from_settings(api_client, user):
    response = _login(api_client, user)
    morsel = response.cookies[settings.AUTH_REFRESH_COOKIE_NAME]

    assert morsel['httponly'] is True
    # http.cookies.Morsel stores boolean flags as '' (falsy) when unset.
    assert bool(morsel['secure']) == settings.AUTH_COOKIE_SECURE
    assert morsel['samesite'] == settings.AUTH_COOKIE_SAMESITE
    assert morsel['path'] == '/api/v1/auth/'


def test_token_refresh_succeeds_with_cookie_and_matching_csrf_header(api_client, user):
    login_response = _login(api_client, user)
    csrf_token = login_response.cookies[settings.AUTH_CSRF_COOKIE_NAME].value

    refresh_response = api_client.post(
        reverse('auth-token-refresh'), format='json', HTTP_X_CSRF_TOKEN=csrf_token
    )

    assert refresh_response.status_code == 200
    assert 'access' in refresh_response.data
    assert 'refresh' not in refresh_response.data
    # ROTATE_REFRESH_TOKENS is True — a new refresh cookie should be issued.
    assert settings.AUTH_REFRESH_COOKIE_NAME in refresh_response.cookies


def test_token_refresh_fails_without_refresh_cookie(api_client):
    response = api_client.post(reverse('auth-token-refresh'), format='json')

    assert response.status_code == 401
    assert response.data['code'] == 'refresh_required'


def test_token_refresh_fails_without_csrf_header(api_client, user):
    _login(api_client, user)

    response = api_client.post(reverse('auth-token-refresh'), format='json')

    assert response.status_code == 403
    assert response.data['code'] == 'csrf_failed'


def test_token_refresh_fails_with_mismatched_csrf_header(api_client, user):
    _login(api_client, user)

    response = api_client.post(
        reverse('auth-token-refresh'), format='json', HTTP_X_CSRF_TOKEN='not-the-real-token'
    )

    assert response.status_code == 403
    assert response.data['code'] == 'csrf_failed'


def test_logout_fails_without_csrf_header(api_client, user):
    login_response = _login(api_client, user)
    access = login_response.data['access']

    response = api_client.post(
        reverse('auth-logout'), format='json', HTTP_AUTHORIZATION=f'Bearer {access}'
    )

    assert response.status_code == 403
    assert response.data['code'] == 'csrf_failed'


def test_logout_clears_both_auth_cookies(api_client, user):
    login_response = _login(api_client, user)
    access = login_response.data['access']
    csrf_token = login_response.cookies[settings.AUTH_CSRF_COOKIE_NAME].value

    response = api_client.post(
        reverse('auth-logout'),
        format='json',
        HTTP_AUTHORIZATION=f'Bearer {access}',
        HTTP_X_CSRF_TOKEN=csrf_token,
    )

    assert response.status_code == 204
    # delete_cookie sets an empty value with an expiry in the past.
    assert response.cookies[settings.AUTH_REFRESH_COOKIE_NAME].value == ''
    assert response.cookies[settings.AUTH_CSRF_COOKIE_NAME].value == ''


def test_register_response_includes_csrf_cookie(api_client):
    response = api_client.post(
        reverse('auth-register'),
        {
            'email': 'cookieflow@example.com',
            'full_name': 'Cookie Flow',
            'password': 'Str0ng!Passw0rd',
            'password_confirm': 'Str0ng!Passw0rd',
        },
        format='json',
    )

    assert response.status_code == 201
    assert settings.AUTH_CSRF_COOKIE_NAME in response.cookies
    assert response.cookies[settings.AUTH_CSRF_COOKIE_NAME]['httponly'] == ''
