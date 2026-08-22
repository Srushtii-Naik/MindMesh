"""Tests for the password reset flow."""

import pytest
from django.core import mail
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from apps.accounts.models import User
from apps.accounts.services import _password_reset_token_generator

pytestmark = pytest.mark.django_db


def test_request_reset_for_existing_email_sends_mail(api_client, user, mailoutbox):
    response = api_client.post(reverse('auth-password-reset'), {'email': user.email}, format='json')

    assert response.status_code == 200
    assert len(mail.outbox) == 1
    assert user.email in mail.outbox[0].to


def test_request_reset_for_unknown_email_returns_generic_200_without_sending_mail(api_client):
    response = api_client.post(
        reverse('auth-password-reset'), {'email': 'ghost@example.com'}, format='json'
    )

    assert response.status_code == 200
    assert len(mail.outbox) == 0


def test_request_reset_response_body_identical_for_known_and_unknown_email(api_client, user):
    """Guards against account enumeration via response content."""
    known = api_client.post(reverse('auth-password-reset'), {'email': user.email}, format='json')
    unknown = api_client.post(
        reverse('auth-password-reset'), {'email': 'ghost@example.com'}, format='json'
    )

    assert known.status_code == unknown.status_code == 200
    assert known.data == unknown.data


def test_confirm_reset_with_valid_token_changes_password(api_client, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = _password_reset_token_generator.make_token(user)

    response = api_client.post(
        reverse('auth-password-reset-confirm'),
        {
            'uid': uid,
            'token': token,
            'new_password': 'BrandNewPassw0rd!',
            'new_password_confirm': 'BrandNewPassw0rd!',
        },
        format='json',
    )

    assert response.status_code == 200
    user.refresh_from_db()
    assert user.check_password('BrandNewPassw0rd!') is True
    assert user.check_password('CorrectHorse123!') is False


def test_confirm_reset_blacklists_existing_sessions(api_client, user):
    from apps.accounts.services import issue_tokens_for_user

    old_tokens = issue_tokens_for_user(user)

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = _password_reset_token_generator.make_token(user)
    api_client.post(
        reverse('auth-password-reset-confirm'),
        {
            'uid': uid,
            'token': token,
            'new_password': 'BrandNewPassw0rd!',
            'new_password_confirm': 'BrandNewPassw0rd!',
        },
        format='json',
    )

    refresh_response = api_client.post(
        reverse('auth-token-refresh'), {'refresh': old_tokens['refresh']}, format='json'
    )
    assert refresh_response.status_code == 401


def test_confirm_reset_with_invalid_token_returns_400(api_client, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    response = api_client.post(
        reverse('auth-password-reset-confirm'),
        {
            'uid': uid,
            'token': 'not-a-real-token',
            'new_password': 'BrandNewPassw0rd!',
            'new_password_confirm': 'BrandNewPassw0rd!',
        },
        format='json',
    )

    assert response.status_code == 400
    assert response.data['code'] == 'invalid_reset_token'


def test_confirm_reset_with_mismatched_passwords_returns_400(api_client, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = _password_reset_token_generator.make_token(user)

    response = api_client.post(
        reverse('auth-password-reset-confirm'),
        {
            'uid': uid,
            'token': token,
            'new_password': 'BrandNewPassw0rd!',
            'new_password_confirm': 'SomethingElse!',
        },
        format='json',
    )

    assert response.status_code == 400


def test_confirm_reset_with_bogus_uid_returns_400(api_client):
    response = api_client.post(
        reverse('auth-password-reset-confirm'),
        {
            'uid': 'not-valid-base64!!',
            'token': 'whatever',
            'new_password': 'BrandNewPassw0rd!',
            'new_password_confirm': 'BrandNewPassw0rd!',
        },
        format='json',
    )

    assert response.status_code == 400
