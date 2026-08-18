"""
Service layer — Notifications (business logic; PROJECT_RULES.md Section 3:
views call services, services never import DRF).

Owns:
  - Notification CRUD/read-state for the in-app notification center.
  - Device token registration for push delivery.
  - The Milestone 9 "reminder engine": scanning due reminders
    (via apps.reminders.services — a cross-domain service interface, never
    a direct model import, per ARCHITECTURE.md Section 3) and turning each
    into a Notification with per-channel deliveries.
  - Per-channel delivery logic (email/push), kept here rather than inline
    in Celery tasks so it's unit-testable independent of Celery's retry
    machinery — the @shared_task wrappers in tasks.py just call these and
    let exceptions propagate for autoretry.
"""

from __future__ import annotations

from datetime import datetime

from django.conf import settings as django_settings
from django.core.mail import send_mail
from django.db.models import QuerySet
from django.utils import timezone

from apps.accounts.models import User
from apps.accounts.services import get_settings_for_user
from apps.notifications.channels import PushDeliveryError, get_push_sender
from apps.notifications.models import (
    DeliveryStatus,
    DevicePlatform,
    DeviceToken,
    Notification,
    NotificationChannel,
    NotificationDelivery,
    NotificationType,
)
from apps.notifications.repositories import (
    count_unread_for_user,
    create_delivery,
    create_device_token,
    create_notification,
    get_device_token,
    get_device_token_for_user,
    get_notification_for_user,
    list_active_device_tokens_for_user,
    list_notifications_for_user,
    mark_all_read_for_user,
    soft_delete_notification,
    update_delivery,
    update_device_token,
    update_notification,
)
from apps.reminders.services import get_due_reminders, mark_reminder_sent


class NotificationNotFoundError(Exception):
    """Raised when a notification cannot be found for the requesting user."""


class DeviceTokenNotFoundError(Exception):
    """Raised when a device token cannot be found for the requesting user."""


# --------------------------------------------------------------------------
# Notification CRUD / read-state (in-app notification center)
# --------------------------------------------------------------------------


def list_notifications_for_user_filtered(
    user: User,
    *,
    is_read: bool | None = None,
    notification_type: str | None = None,
) -> QuerySet[Notification]:
    queryset = list_notifications_for_user(user)
    if is_read is not None:
        queryset = queryset.filter(is_read=is_read)
    if notification_type:
        queryset = queryset.filter(notification_type=notification_type)
    return queryset


def get_notification(user: User, notification_id) -> Notification:
    notification = get_notification_for_user(user, notification_id)
    if notification is None:
        raise NotificationNotFoundError('Notification not found.')
    return notification


def get_unread_count_for_user(user: User) -> int:
    return count_unread_for_user(user)


def update_notification_read_state(user: User, notification_id, *, is_read: bool) -> Notification:
    notification = get_notification_for_user(user, notification_id)
    if notification is None:
        raise NotificationNotFoundError('Notification not found.')
    return update_notification(
        notification, is_read=is_read, read_at=timezone.now() if is_read else None
    )


def mark_all_notifications_read(user: User) -> int:
    return mark_all_read_for_user(user)


def delete_notification_for_user(user: User, notification_id) -> None:
    notification = get_notification_for_user(user, notification_id)
    if notification is None:
        raise NotificationNotFoundError('Notification not found.')
    soft_delete_notification(notification)


# --------------------------------------------------------------------------
# Notification creation + per-channel dispatch
# --------------------------------------------------------------------------


def create_notification_for_user(
    user: User,
    *,
    notification_type: str,
    title: str,
    message: str = '',
    reminder=None,
    channels: list[str] | None = None,
) -> Notification:
    """
    Creates a Notification and a NotificationDelivery per requested channel,
    then dispatches each delivery. IN_APP is "delivered" the moment the row
    exists (there's nothing further to send), so it's marked sent inline;
    EMAIL and PUSH are handed off to their Celery tasks.
    """
    notification = create_notification(
        user=user,
        notification_type=notification_type,
        title=title.strip(),
        message=message,
        reminder=reminder,
    )

    for channel in dict.fromkeys(channels or [NotificationChannel.IN_APP]):
        delivery = create_delivery(notification=notification, channel=channel)
        _dispatch_delivery(delivery)

    return notification


def _dispatch_delivery(delivery: NotificationDelivery) -> None:
    if delivery.channel == NotificationChannel.IN_APP:
        mark_delivery_sent(delivery)
        return

    # Imported here (not at module top) to avoid a circular import between
    # services.py and tasks.py, which both import from each other's module.
    from apps.notifications.tasks import (
        deliver_notification_email_task,
        deliver_notification_push_task,
    )

    if delivery.channel == NotificationChannel.EMAIL:
        deliver_notification_email_task.delay(delivery_id=str(delivery.id))
    elif delivery.channel == NotificationChannel.PUSH:
        deliver_notification_push_task.delay(delivery_id=str(delivery.id))


def mark_delivery_sent(delivery: NotificationDelivery) -> NotificationDelivery:
    return update_delivery(delivery, status=DeliveryStatus.SENT, sent_at=timezone.now(), error_message='')


def mark_delivery_failed(delivery: NotificationDelivery, *, error_message: str) -> NotificationDelivery:
    """Marks a delivery failed and *keeps* the error on the record — the
    ROADMAP.md requirement that 'delivery failures are retried/logged, not
    silently dropped' means the failure has to be visible somewhere after
    retries are exhausted, not just raised-and-forgotten."""
    return update_delivery(delivery, status=DeliveryStatus.FAILED, error_message=error_message)


def deliver_email_notification(delivery: NotificationDelivery) -> None:
    """
    Sends `delivery`'s parent notification by email and updates its status.
    Respects the user's UserSettings.email_notifications_enabled toggle at
    the call site (dispatch_due_reminder_notifications only *requests* the
    EMAIL channel when it's enabled) rather than here, so this function
    stays a pure "send it" primitive reusable by any future email-channel
    caller.

    Raises on failure (after marking the delivery failed) so the calling
    Celery task's autoretry_for can retry it.
    """
    notification = delivery.notification
    try:
        send_mail(
            subject=notification.title,
            message=notification.message or notification.title,
            from_email=django_settings.DEFAULT_FROM_EMAIL,
            recipient_list=[notification.user.email],
            fail_silently=False,
        )
    except Exception as exc:
        mark_delivery_failed(delivery, error_message=str(exc))
        raise
    mark_delivery_sent(delivery)


def deliver_push_notification(delivery: NotificationDelivery) -> None:
    """
    Sends `delivery`'s parent notification to every active device token the
    user has registered. A notification with no registered devices, or
    where every device's send fails, is marked failed (and raises so the
    Celery task can retry); a partial success (some devices succeeded) is
    still marked sent, with the failed devices' errors preserved so they're
    not silently dropped.
    """
    notification = delivery.notification
    tokens = list(list_active_device_tokens_for_user(notification.user))
    if not tokens:
        mark_delivery_failed(delivery, error_message='No active device tokens registered.')
        return

    sender = get_push_sender()
    errors: list[str] = []
    for device in tokens:
        try:
            sender.send(token=device.token, title=notification.title, body=notification.message)
        except Exception as exc:  # noqa: BLE001 - one bad token shouldn't fail the rest
            errors.append(f'{device.id}: {exc}')

    if len(errors) == len(tokens):
        error_message = '; '.join(errors)
        mark_delivery_failed(delivery, error_message=error_message)
        raise PushDeliveryError(error_message)

    mark_delivery_sent(delivery)
    if errors:
        # Partial failure: overall delivery succeeded, but keep a record of
        # which devices didn't get it instead of dropping that information.
        update_delivery(delivery, error_message='; '.join(errors))


# --------------------------------------------------------------------------
# Reminder engine (Milestone 9's Celery Beat-driven scan)
# --------------------------------------------------------------------------


def dispatch_due_reminder_notifications(*, now: datetime | None = None) -> int:
    """
    The Milestone 9 reminder-delivery engine
    (ROADMAP.md: "Reminder engine runs on scheduled Celery tasks and fires
    accurately"). Invoked by the Celery Beat task registered in
    apps.notifications.tasks.scan_due_reminders_task.

    For each reminder due at or before `now`:
      - the reminder is marked sent *before* the notification is created,
        so a failure partway through this loop can never re-fire the same
        reminder on the next scan and duplicate-notify the user (the
        alternative — marking sent last — risks exactly that on retry,
        which is the worse failure mode for a notification system);
      - a Notification is created with IN_APP always included, EMAIL
        included only if the user's UserSettings.email_notifications_enabled
        is set, and PUSH included only if the user has an active device
        token registered.

    Returns the number of reminders processed.
    """
    due_reminders = get_due_reminders(now)
    processed = 0

    for reminder in due_reminders:
        user = reminder.user
        mark_reminder_sent(reminder)

        channels = [NotificationChannel.IN_APP]
        if get_settings_for_user(user).email_notifications_enabled:
            channels.append(NotificationChannel.EMAIL)
        if list_active_device_tokens_for_user(user).exists():
            channels.append(NotificationChannel.PUSH)

        create_notification_for_user(
            user,
            notification_type=NotificationType.REMINDER,
            title=reminder.title,
            message=reminder.message,
            reminder=reminder,
            channels=channels,
        )
        processed += 1

    return processed


# --------------------------------------------------------------------------
# Device tokens (push registration)
# --------------------------------------------------------------------------


def register_device_token_for_user(
    user: User, *, token: str, platform: str = DevicePlatform.WEB
) -> DeviceToken:
    """
    Registers (or re-associates) a push device token for `user`.

    Tokens are globally unique (a browser/device push subscription
    identifier assigned by the platform, not by us), so a token previously
    registered to a *different* user is re-pointed at the current user
    rather than raising a unique-constraint error — see DeviceToken's
    docstring for why that's the correct real-world behavior.
    """
    existing = get_device_token(token)
    if existing is None:
        return create_device_token(user=user, token=token, platform=platform)
    return update_device_token(existing, user=user, platform=platform, is_active=True)


def unregister_device_token_for_user(user: User, device_id) -> None:
    device = get_device_token_for_user(user, device_id)
    if device is None:
        raise DeviceTokenNotFoundError('Device token not found.')
    update_device_token(device, is_active=False)
