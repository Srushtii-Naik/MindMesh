"""Unit tests — apps.notifications.services (business logic, independent of
DRF/Celery, per PROJECT_RULES.md testing rules)."""

from unittest.mock import patch

import pytest
from django.core import mail

from apps.notifications.channels import PushDeliveryError
from apps.notifications.models import (
    DeliveryStatus,
    DevicePlatform,
    Notification,
    NotificationChannel,
    NotificationType,
)
from apps.notifications.services import (
    DeviceTokenNotFoundError,
    NotificationNotFoundError,
    create_notification_for_user,
    delete_notification_for_user,
    deliver_email_notification,
    deliver_push_notification,
    get_notification,
    get_unread_count_for_user,
    list_notifications_for_user_filtered,
    mark_all_notifications_read,
    register_device_token_for_user,
    unregister_device_token_for_user,
    update_notification_read_state,
)

pytestmark = pytest.mark.django_db


# --------------------------------------------------------------------------
# create_notification_for_user / channel dispatch
# --------------------------------------------------------------------------


def test_create_notification_with_in_app_channel_marks_delivery_sent_immediately(user):
    notification = create_notification_for_user(
        user,
        notification_type=NotificationType.SYSTEM,
        title='  Hello  ',
        message='Body text',
        channels=[NotificationChannel.IN_APP],
    )

    assert notification.title == 'Hello'
    deliveries = list(notification.deliveries.all())
    assert len(deliveries) == 1
    assert deliveries[0].channel == NotificationChannel.IN_APP
    assert deliveries[0].status == DeliveryStatus.SENT
    assert deliveries[0].sent_at is not None


def test_create_notification_with_email_channel_sends_mail_and_marks_sent(user):
    notification = create_notification_for_user(
        user,
        notification_type=NotificationType.SYSTEM,
        title='Reminder',
        message='Body',
        channels=[NotificationChannel.EMAIL],
    )

    assert len(mail.outbox) == 1
    assert user.email in mail.outbox[0].to

    delivery = notification.deliveries.get(channel=NotificationChannel.EMAIL)
    assert delivery.status == DeliveryStatus.SENT


def test_create_notification_deduplicates_channels(user):
    notification = create_notification_for_user(
        user,
        notification_type=NotificationType.SYSTEM,
        title='Dup',
        channels=[NotificationChannel.IN_APP, NotificationChannel.IN_APP],
    )
    assert notification.deliveries.count() == 1


def test_create_notification_defaults_to_in_app_channel(user):
    notification = create_notification_for_user(
        user, notification_type=NotificationType.SYSTEM, title='Default channel'
    )
    assert notification.deliveries.count() == 1
    assert notification.deliveries.first().channel == NotificationChannel.IN_APP


# --------------------------------------------------------------------------
# Notification CRUD / read-state
# --------------------------------------------------------------------------


def test_get_notification_raises_for_other_user(notification, other_user):
    with pytest.raises(NotificationNotFoundError):
        get_notification(other_user, notification.id)


def test_update_notification_read_state_sets_read_at(user, notification):
    updated = update_notification_read_state(user, notification.id, is_read=True)
    assert updated.is_read is True
    assert updated.read_at is not None

    unread_again = update_notification_read_state(user, notification.id, is_read=False)
    assert unread_again.is_read is False
    assert unread_again.read_at is None


def test_mark_all_notifications_read(user):
    create_notification_for_user(user, notification_type=NotificationType.SYSTEM, title='One')
    create_notification_for_user(user, notification_type=NotificationType.SYSTEM, title='Two')

    updated_count = mark_all_notifications_read(user)

    assert updated_count == 2
    assert get_unread_count_for_user(user) == 0


def test_get_unread_count_for_user(user):
    create_notification_for_user(user, notification_type=NotificationType.SYSTEM, title='One')
    n2 = create_notification_for_user(user, notification_type=NotificationType.SYSTEM, title='Two')
    update_notification_read_state(user, n2.id, is_read=True)

    assert get_unread_count_for_user(user) == 1


def test_delete_notification_for_user_soft_deletes(user, notification):
    delete_notification_for_user(user, notification.id)

    assert Notification.objects.filter(id=notification.id, is_active=True).count() == 0
    assert Notification.objects.filter(id=notification.id, is_active=False).count() == 1

    with pytest.raises(NotificationNotFoundError):
        get_notification(user, notification.id)


def test_delete_notification_for_user_raises_for_other_user(notification, other_user):
    with pytest.raises(NotificationNotFoundError):
        delete_notification_for_user(other_user, notification.id)


def test_list_notifications_for_user_filtered_by_is_read(user):
    n1 = create_notification_for_user(user, notification_type=NotificationType.SYSTEM, title='One')
    create_notification_for_user(user, notification_type=NotificationType.SYSTEM, title='Two')
    update_notification_read_state(user, n1.id, is_read=True)

    unread = list_notifications_for_user_filtered(user, is_read=False)
    assert unread.count() == 1
    assert unread.first().title == 'Two'


def test_list_notifications_for_user_filtered_by_type(user):
    create_notification_for_user(user, notification_type=NotificationType.SYSTEM, title='System one')
    create_notification_for_user(user, notification_type=NotificationType.REMINDER, title='Reminder one')

    reminders = list_notifications_for_user_filtered(user, notification_type=NotificationType.REMINDER)
    assert reminders.count() == 1
    assert reminders.first().title == 'Reminder one'


# --------------------------------------------------------------------------
# Device tokens
# --------------------------------------------------------------------------


def test_register_device_token_creates_new_token(user):
    device = register_device_token_for_user(user, token='abc123', platform=DevicePlatform.WEB)
    assert device.user_id == user.id
    assert device.is_active is True


def test_register_device_token_reactivates_and_reassigns_existing_token(user, other_user):
    device = register_device_token_for_user(other_user, token='shared-token')
    unregister_device_token_for_user(other_user, device.id)

    reassigned = register_device_token_for_user(user, token='shared-token', platform=DevicePlatform.IOS)

    assert reassigned.id == device.id
    assert reassigned.user_id == user.id
    assert reassigned.platform == DevicePlatform.IOS
    assert reassigned.is_active is True


def test_unregister_device_token_deactivates(user):
    device = register_device_token_for_user(user, token='abc123')
    unregister_device_token_for_user(user, device.id)

    device.refresh_from_db()
    assert device.is_active is False


def test_unregister_device_token_raises_for_other_user(user, other_user):
    device = register_device_token_for_user(user, token='abc123')
    with pytest.raises(DeviceTokenNotFoundError):
        unregister_device_token_for_user(other_user, device.id)


# --------------------------------------------------------------------------
# Channel delivery primitives
# --------------------------------------------------------------------------


def test_deliver_email_notification_marks_failed_and_raises_on_error(user, notification):
    delivery = notification.deliveries.create(channel=NotificationChannel.EMAIL)

    with patch('apps.notifications.services.send_mail', side_effect=RuntimeError('SMTP down')):
        with pytest.raises(RuntimeError):
            deliver_email_notification(delivery)

    delivery.refresh_from_db()
    assert delivery.status == DeliveryStatus.FAILED
    assert 'SMTP down' in delivery.error_message


def test_deliver_push_notification_fails_with_no_registered_devices(user, notification):
    delivery = notification.deliveries.create(channel=NotificationChannel.PUSH)

    deliver_push_notification(delivery)

    delivery.refresh_from_db()
    assert delivery.status == DeliveryStatus.FAILED
    assert 'No active device tokens' in delivery.error_message


def test_deliver_push_notification_succeeds_with_registered_device(user, notification):
    register_device_token_for_user(user, token='device-1')
    delivery = notification.deliveries.create(channel=NotificationChannel.PUSH)

    deliver_push_notification(delivery)

    delivery.refresh_from_db()
    assert delivery.status == DeliveryStatus.SENT


def test_deliver_push_notification_fails_and_raises_when_every_device_fails(user, notification):
    register_device_token_for_user(user, token='device-1')
    delivery = notification.deliveries.create(channel=NotificationChannel.PUSH)

    with patch(
        'apps.notifications.services.get_push_sender'
    ) as mock_get_sender:
        mock_get_sender.return_value.send.side_effect = RuntimeError('vendor unreachable')
        with pytest.raises(PushDeliveryError):
            deliver_push_notification(delivery)

    delivery.refresh_from_db()
    assert delivery.status == DeliveryStatus.FAILED
    assert 'vendor unreachable' in delivery.error_message


def test_deliver_push_notification_partial_failure_still_marks_sent(user, notification):
    register_device_token_for_user(user, token='device-1')
    register_device_token_for_user(user, token='device-2')
    delivery = notification.deliveries.create(channel=NotificationChannel.PUSH)

    call_count = {'n': 0}

    def flaky_send(*, token, title, body):
        call_count['n'] += 1
        if call_count['n'] == 1:
            raise RuntimeError('one bad device')

    with patch('apps.notifications.services.get_push_sender') as mock_get_sender:
        mock_get_sender.return_value.send.side_effect = flaky_send
        deliver_push_notification(delivery)

    delivery.refresh_from_db()
    assert delivery.status == DeliveryStatus.SENT
    assert 'one bad device' in delivery.error_message
