"""Tests for session management endpoints (list / revoke / revoke-all)."""

import pytest
from django.urls import reverse

from apps.accounts.services import issue_tokens_for_user

pytestmark = pytest.mark.django_db


def test_list_sessions_requires_authentication(api_client):
    response = api_client.get(reverse('auth-sessions'))
    assert response.status_code == 401


def test_list_sessions_returns_active_sessions_for_current_user(auth_client, user):
    # auth_client fixture already issued one token pair for `user`; issue a second.
    issue_tokens_for_user(user)

    response = auth_client.get(reverse('auth-sessions'))

    assert response.status_code == 200
    assert len(response.data) == 2


def test_list_sessions_does_not_include_other_users_sessions(auth_client, other_user):
    issue_tokens_for_user(other_user)

    response = auth_client.get(reverse('auth-sessions'))

    assert response.status_code == 200
    assert len(response.data) == 1


def test_revoke_session_blacklists_it(auth_client, user):
    from rest_framework_simplejwt.token_blacklist.models import OutstandingToken

    session_id = OutstandingToken.objects.get(user=user).id

    response = auth_client.post(reverse('auth-session-revoke', args=[session_id]))
    assert response.status_code == 204

    list_response = auth_client.get(reverse('auth-sessions'))
    assert len(list_response.data) == 0


def test_revoke_session_cannot_target_another_users_session(auth_client, other_user):
    from rest_framework_simplejwt.token_blacklist.models import OutstandingToken

    issue_tokens_for_user(other_user)
    other_session_id = OutstandingToken.objects.get(user=other_user).id

    response = auth_client.post(reverse('auth-session-revoke', args=[other_session_id]))
    assert response.status_code == 404


def test_revoke_all_sessions_blacklists_every_session(auth_client, user):
    issue_tokens_for_user(user)
    issue_tokens_for_user(user)

    response = auth_client.post(reverse('auth-sessions-revoke-all'))
    assert response.status_code == 204

    list_response = auth_client.get(reverse('auth-sessions'))
    assert len(list_response.data) == 0


def test_revoke_all_sessions_forces_current_refresh_token_to_fail(api_client, user):
    tokens = issue_tokens_for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')

    api_client.post(reverse('auth-sessions-revoke-all'))

    refresh_response = api_client.post(
        reverse('auth-token-refresh'), {'refresh': tokens['refresh']}, format='json'
    )
    assert refresh_response.status_code == 401
