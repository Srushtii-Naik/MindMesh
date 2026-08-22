"""
Repository / data-access layer — Notifications.

Encapsulates ORM queries for Notification, NotificationDelivery, and
DeviceToken, isolating persistence details from the service layer, per
ARCHITECTURE.md Section 3. Every notification/device-token query here is
scoped to a given user — row-level ownership per PROJECT_RULES.md Section 7.
"""

from django.db.models import QuerySet
from django.utils import timezone

from apps.accounts.models import User
from apps.notifications.models import DeviceToken, Notification, NotificationDelivery

# --------------------------------------------------------------------------
# Notification
# --------------------------------------------------------------------------


def list_notifications_for_user(user: User) -> QuerySet[Notification]:
    """Base queryset of the user's non-deleted notifications. Filters applied
    by the service layer."""
    return Notification.objects.filter(user=user, is_active=True)


def get_notification_for_user(user: User, notification_id) -> Notification | None:
    return Notification.objects.filter(user=user, id=notification_id, is_active=True).first()


def create_notification(*, user: User, **fields) -> Notification:
    return Notification.objects.create(user=user, **fields)


def update_notification(notification: Notification, **fields) -> Notification:
    for field, value in fields.items():
        setattr(notification, field, value)
    notification.save()
    return notification


def soft_delete_notification(notification: Notification) -> None:
    notification.is_active = False
    notification.deleted_at = timezone.now()
    notification.save(update_fields=['is_active', 'deleted_at', 'updated_at'])


def count_unread_for_user(user: User) -> int:
    return list_notifications_for_user(user).filter(is_read=False).count()


def mark_all_read_for_user(user: User) -> int:
    """Bulk-marks every unread notification read. Uses `.update()` rather
    than per-row `.save()` for efficiency; `updated_at` is set explicitly
    since `auto_now` doesn't fire on bulk `.update()` calls."""
    now = timezone.now()
    return (
        list_notifications_for_user(user)
        .filter(is_read=False)
        .update(is_read=True, read_at=now, updated_at=now)
    )


# --------------------------------------------------------------------------
# NotificationDelivery
# --------------------------------------------------------------------------


def create_delivery(*, notification: Notification, channel: str, **fields) -> NotificationDelivery:
    return NotificationDelivery.objects.create(notification=notification, channel=channel, **fields)


def update_delivery(delivery: NotificationDelivery, **fields) -> NotificationDelivery:
    for field, value in fields.items():
        setattr(delivery, field, value)
    delivery.save()
    return delivery


# --------------------------------------------------------------------------
# DeviceToken
# --------------------------------------------------------------------------


def get_device_token(token: str) -> DeviceToken | None:
    """Looked up by token alone (globally unique), not scoped to a user —
    used by registration, which may need to re-associate a token with a
    *different* user than currently owns it. See DeviceToken's docstring."""
    return DeviceToken.objects.filter(token=token).first()


def get_device_token_for_user(user: User, device_id) -> DeviceToken | None:
    return DeviceToken.objects.filter(user=user, id=device_id).first()


def create_device_token(*, user: User, token: str, platform: str) -> DeviceToken:
    return DeviceToken.objects.create(user=user, token=token, platform=platform)


def update_device_token(device: DeviceToken, **fields) -> DeviceToken:
    for field, value in fields.items():
        setattr(device, field, value)
    device.save()
    return device


def list_active_device_tokens_for_user(user: User) -> QuerySet[DeviceToken]:
    return DeviceToken.objects.filter(user=user, is_active=True)
