"""
DRF serializers — Notifications. Request parsing/validation and response
shaping only; no business logic (PROJECT_RULES.md Section 3).
"""

from rest_framework import serializers

from apps.notifications.models import (
    DevicePlatform,
    DeviceToken,
    Notification,
    NotificationDelivery,
)


class NotificationDeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationDelivery
        fields = ['id', 'channel', 'status', 'error_message', 'sent_at', 'created_at']
        read_only_fields = fields


class LinkedReminderSerializer(serializers.Serializer):
    """Minimal read-only view of a Notification's source reminder, if any."""

    id = serializers.UUIDField()
    title = serializers.CharField()


class NotificationSerializer(serializers.ModelSerializer):
    reminder = LinkedReminderSerializer(read_only=True)
    deliveries = NotificationDeliverySerializer(many=True, read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id',
            'notification_type',
            'title',
            'message',
            'reminder',
            'is_read',
            'read_at',
            'deliveries',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields


class NotificationUpdateSerializer(serializers.Serializer):
    is_read = serializers.BooleanField()


class DeviceTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceToken
        fields = ['id', 'token', 'platform', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'is_active', 'created_at', 'updated_at']


class DeviceTokenWriteSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=512, trim_whitespace=True, allow_blank=False)
    platform = serializers.ChoiceField(
        choices=DevicePlatform.choices, required=False, default=DevicePlatform.WEB
    )
