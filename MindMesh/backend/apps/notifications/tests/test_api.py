"""API tests — apps.notifications.views, exercised through the DRF test
client per the existing app convention (see apps/reminders/tests)."""

import pytest
from django.urls import reverse

from apps.notifications.models import NotificationType
from apps.notifications.services import (
    create_notification_for_user,
    register_device_token_for_user,
)

pytestmark = pytest.mark.django_db


# --------------------------------------------------------------------------
# List / filter / pagination
# --------------------------------------------------------------------------


def test_list_notifications_requires_auth(api_client):
    response = api_client.get(reverse('notification-list'))
    assert response.status_code == 401


def test_list_notifications_returns_only_own_notifications(auth_client, user, other_user):
    create_notification_for_user(user, notification_type=NotificationType.SYSTEM, title='Mine')
    create_notification_for_user(other_user, notification_type=NotificationType.SYSTEM, title='Not mine')

    response = auth_client.get(reverse('notification-list'))

    assert response.status_code == 200
    titles = [item['title'] for item in response.data['results']]
    assert titles == ['Mine']


def test_list_notifications_filters_by_is_read(auth_client, user):
    n1 = create_notification_for_user(user, notification_type=NotificationType.SYSTEM, title='Read me')
    create_notification_for_user(user, notification_type=NotificationType.SYSTEM, title='Unread')
    auth_client.patch(reverse('notification-detail', args=[n1.id]), {'is_read': True}, format='json')

    response = auth_client.get(reverse('notification-list'), {'is_read': 'false'})

    assert response.status_code == 200
    titles = [item['title'] for item in response.data['results']]
    assert titles == ['Unread']


def test_list_notifications_rejects_invalid_is_read_filter(auth_client):
    response = auth_client.get(reverse('notification-list'), {'is_read': 'maybe'})
    assert response.status_code == 400
    assert response.data['code'] == 'invalid_filter'


def test_list_notifications_filters_by_type(auth_client, user):
    create_notification_for_user(user, notification_type=NotificationType.SYSTEM, title='Sys')
    create_notification_for_user(user, notification_type=NotificationType.REMINDER, title='Rem')

    response = auth_client.get(reverse('notification-list'), {'notification_type': 'reminder'})

    titles = [item['title'] for item in response.data['results']]
    assert titles == ['Rem']


# --------------------------------------------------------------------------
# Unread count / mark all read
# --------------------------------------------------------------------------


def test_unread_count(auth_client, user):
    create_notification_for_user(user, notification_type=NotificationType.SYSTEM, title='One')
    create_notification_for_user(user, notification_type=NotificationType.SYSTEM, title='Two')

    response = auth_client.get(reverse('notification-unread-count'))

    assert response.status_code == 200
    assert response.data['unread_count'] == 2


def test_mark_all_read(auth_client, user):
    create_notification_for_user(user, notification_type=NotificationType.SYSTEM, title='One')
    create_notification_for_user(user, notification_type=NotificationType.SYSTEM, title='Two')

    response = auth_client.post(reverse('notification-mark-all-read'))

    assert response.status_code == 200
    assert response.data['updated'] == 2

    unread_response = auth_client.get(reverse('notification-unread-count'))
    assert unread_response.data['unread_count'] == 0


# --------------------------------------------------------------------------
# Detail: get / patch / delete
# --------------------------------------------------------------------------


def test_get_notification_detail(auth_client, notification):
    response = auth_client.get(reverse('notification-detail', args=[notification.id]))
    assert response.status_code == 200
    assert response.data['id'] == str(notification.id)
    assert 'deliveries' in response.data


def test_get_notification_detail_404_for_other_user(api_client, other_user, notification):
    from apps.accounts.services import issue_tokens_for_user

    tokens = issue_tokens_for_user(other_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')

    response = api_client.get(reverse('notification-detail', args=[notification.id]))
    assert response.status_code == 404
    assert response.data['code'] == 'notification_not_found'


def test_patch_notification_marks_read(auth_client, notification):
    response = auth_client.patch(
        reverse('notification-detail', args=[notification.id]), {'is_read': True}, format='json'
    )
    assert response.status_code == 200
    assert response.data['is_read'] is True
    assert response.data['read_at'] is not None


def test_delete_notification_soft_deletes(auth_client, notification):
    response = auth_client.delete(reverse('notification-detail', args=[notification.id]))
    assert response.status_code == 204

    get_response = auth_client.get(reverse('notification-detail', args=[notification.id]))
    assert get_response.status_code == 404


# --------------------------------------------------------------------------
# Device tokens
# --------------------------------------------------------------------------


def test_register_device_token(auth_client):
    response = auth_client.post(
        reverse('device-token-list'), {'token': 'abc123', 'platform': 'web'}, format='json'
    )
    assert response.status_code == 201
    assert response.data['token'] == 'abc123'
    assert response.data['is_active'] is True


def test_register_device_token_requires_token(auth_client):
    response = auth_client.post(reverse('device-token-list'), {}, format='json')
    assert response.status_code == 400


def test_unregister_device_token(auth_client, user):
    device = register_device_token_for_user(user, token='abc123')

    response = auth_client.delete(reverse('device-token-detail', args=[device.id]))

    assert response.status_code == 204
    device.refresh_from_db()
    assert device.is_active is False


def test_unregister_device_token_404_for_other_user(api_client, user, other_user):
    from apps.accounts.services import issue_tokens_for_user

    device = register_device_token_for_user(user, token='abc123')
    tokens = issue_tokens_for_user(other_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')

    response = api_client.delete(reverse('device-token-detail', args=[device.id]))
    assert response.status_code == 404
    assert response.data['code'] == 'device_token_not_found'
