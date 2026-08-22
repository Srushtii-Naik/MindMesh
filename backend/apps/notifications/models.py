"""
Domain models — Notifications.

Per ROADMAP.md Milestone 9, this milestone delivers the full notification
system: the reminder-delivery engine (building on Milestone 5's Reminder
data model), push and email delivery, and the in-app notification center.
This mirrors ARCHITECTURE.md Section 4's "Notifications — notification
records, delivery status, channel (push/email/in-app)" entity group.

`Notification` is the logical, in-app-visible record ("MindMesh told you
X"). `NotificationDelivery` tracks *per-channel* delivery status for that
notification, so a single notification can be sent in-app, by email, and by
push independently, with independent success/failure/retry tracking — per
PROJECT_RULES.md Section 12/ROADMAP.md's "Delivery failures are retried/
logged, not silently dropped."
"""

import uuid

from django.conf import settings
from django.db import models


class NotificationType(models.TextChoices):
    """
    What triggered the notification. Only REMINDER is actually produced by
    this milestone (ROADMAP.md Milestone 9's reminder engine); SYSTEM exists
    for account-level/admin-originated notifications and is kept deliberately
    generic rather than speculatively adding task/event trigger types this
    milestone doesn't build a producer for.
    """

    REMINDER = 'reminder', 'Reminder'
    SYSTEM = 'system', 'System'


class NotificationChannel(models.TextChoices):
    IN_APP = 'in_app', 'In-App'
    EMAIL = 'email', 'Email'
    PUSH = 'push', 'Push'


class DeliveryStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    SENT = 'sent', 'Sent'
    FAILED = 'failed', 'Failed'


class DevicePlatform(models.TextChoices):
    WEB = 'web', 'Web'
    IOS = 'ios', 'iOS'
    ANDROID = 'android', 'Android'


class Notification(models.Model):
    """A user-owned notification, optionally linked back to the reminder
    that produced it."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications'
    )

    notification_type = models.CharField(
        max_length=20, choices=NotificationType.choices, default=NotificationType.SYSTEM
    )
    title = models.CharField(max_length=255)
    message = models.TextField(blank=True, default='')

    reminder = models.ForeignKey(
        'reminders.Reminder',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications',
    )

    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    # Soft delete (PROJECT_RULES.md Section 7).
    is_active = models.BooleanField(default=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notifications_notification'
        ordering = ['-created_at']
        verbose_name = 'notification'
        verbose_name_plural = 'notifications'
        indexes = [
            models.Index(fields=['user', 'is_active', 'is_read']),
            models.Index(fields=['user', 'is_active', 'created_at']),
        ]

    def __str__(self) -> str:
        return self.title


class NotificationDelivery(models.Model):
    """Per-channel delivery attempt/status for a Notification."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    notification = models.ForeignKey(
        Notification, on_delete=models.CASCADE, related_name='deliveries'
    )
    channel = models.CharField(max_length=10, choices=NotificationChannel.choices)
    status = models.CharField(
        max_length=10, choices=DeliveryStatus.choices, default=DeliveryStatus.PENDING
    )
    error_message = models.TextField(blank=True, default='')
    sent_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notifications_delivery'
        ordering = ['-created_at']
        verbose_name = 'notification delivery'
        verbose_name_plural = 'notification deliveries'
        indexes = [
            models.Index(fields=['notification', 'channel']),
            models.Index(fields=['status']),
        ]

    def __str__(self) -> str:
        return f'{self.notification_id} via {self.channel} ({self.status})'


class DeviceToken(models.Model):
    """
    A registered push-delivery target for a user (ARCHITECTURE.md Section 4
    Notifications entity group's push channel).

    Kept as its own model rather than a field on User/UserSettings, since a
    user may have several devices (e.g. a phone and a browser) each needing
    independent registration/revocation. `token` is globally unique (it's
    the push provider's own subscription identifier); re-registering an
    existing token re-associates it with the requesting user rather than
    erroring, since the same physical device's token can legitimately move
    between accounts (e.g. sign-out/sign-in as a different user on a shared
    device) — see apps.notifications.services.register_device_token_for_user.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='device_tokens'
    )
    token = models.CharField(max_length=512, unique=True)
    platform = models.CharField(
        max_length=10, choices=DevicePlatform.choices, default=DevicePlatform.WEB
    )
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notifications_device_token'
        ordering = ['-created_at']
        verbose_name = 'device token'
        verbose_name_plural = 'device tokens'
        indexes = [models.Index(fields=['user', 'is_active'])]

    def __str__(self) -> str:
        return f'{self.user_id} ({self.platform})'
