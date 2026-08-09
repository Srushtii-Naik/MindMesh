"""
Tests for auth-endpoint rate limiting (Milestone 2.2, PROJECT_RULES.md
Section 8 -- "Rate limiting on auth ... endpoints at minimum").

DRF's `ScopedRateThrottle` reads `DEFAULT_THROTTLE_RATES` into a class
attribute once, at import time, rather than re-reading Django settings per
request -- so `override_settings(REST_FRAMEWORK=...)` does not take effect
for it. Instead, each test temporarily patches the relevant scope's rate
directly via `monkeypatch.setitem`, which pytest reverts automatically.

The cache is cleared before/after each test so results aren't affected by
request counts from other tests sharing the same in-process LocMemCache
(config/settings/test.py).
"""

from unittest.mock import patch

import pytest
from django.core.cache import cache
from django.urls import reverse
from rest_framework.throttling import ScopedRateThrottle

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def clear_throttle_cache():
    cache.clear()
    yield
    cache.clear()


def test_login_endpoint_is_rate_limited(api_client, user, monkeypatch):
    monkeypatch.setitem(ScopedRateThrottle.THROTTLE_RATES, 'auth_login', '2/min')
    payload = {'email': user.email, 'password': 'wrong-password'}

    for _ in range(2):
        response = api_client.post(reverse('auth-login'), payload, format='json')
        assert response.status_code == 401

    throttled = api_client.post(reverse('auth-login'), payload, format='json')
    assert throttled.status_code == 429


def test_register_endpoint_is_rate_limited(api_client, monkeypatch):
    monkeypatch.setitem(ScopedRateThrottle.THROTTLE_RATES, 'auth_register', '1/min')
    payload = {
        'email': 'first@example.com',
        'full_name': 'First User',
        'password': 'CorrectHorse123!',
        'password_confirm': 'CorrectHorse123!',
    }

    first = api_client.post(reverse('auth-register'), payload, format='json')
    assert first.status_code == 201

    second = api_client.post(
        reverse('auth-register'),
        {**payload, 'email': 'second@example.com'},
        format='json',
    )
    assert second.status_code == 429


def test_password_reset_request_endpoint_is_rate_limited(api_client, user, monkeypatch):
    monkeypatch.setitem(ScopedRateThrottle.THROTTLE_RATES, 'auth_password_reset', '1/min')

    first = api_client.post(
        reverse('auth-password-reset'), {'email': user.email}, format='json'
    )
    assert first.status_code == 200

    second = api_client.post(
        reverse('auth-password-reset'), {'email': user.email}, format='json'
    )
    assert second.status_code == 429


@patch('apps.accounts.services.google_id_token.verify_oauth2_token')
def test_google_endpoint_is_rate_limited(mock_verify, api_client, monkeypatch):
    monkeypatch.setitem(ScopedRateThrottle.THROTTLE_RATES, 'auth_google', '1/min')
    mock_verify.side_effect = ValueError('Token expired')

    first = api_client.post(reverse('auth-google'), {'id_token': 'not-a-real-token'}, format='json')
    assert first.status_code == 401  # invalid token, but not throttled yet

    second = api_client.post(reverse('auth-google'), {'id_token': 'not-a-real-token'}, format='json')
    assert second.status_code == 429


def test_token_refresh_endpoint_is_rate_limited(api_client, monkeypatch):
    monkeypatch.setitem(ScopedRateThrottle.THROTTLE_RATES, 'auth_token_refresh', '1/min')

    first = api_client.post(reverse('auth-token-refresh'), {'refresh': 'not-a-real-token'}, format='json')
    assert first.status_code == 401  # invalid token, but not throttled yet

    second = api_client.post(reverse('auth-token-refresh'), {'refresh': 'not-a-real-token'}, format='json')
    assert second.status_code == 429


def test_profile_endpoint_is_not_scoped_and_therefore_unthrottled(auth_client):
    """
    Sanity check that ScopedRateThrottle's opt-in design (no `throttle_scope`
    on ProfileView) leaves non-auth-critical endpoints unaffected, per the
    "at minimum" scope in PROJECT_RULES.md Section 8.
    """
    for _ in range(15):
        response = auth_client.get(reverse('auth-profile'))
        assert response.status_code == 200
