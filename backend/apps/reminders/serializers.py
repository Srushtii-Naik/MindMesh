"""
DRF serializers — Reminders.

Handle request parsing/validation and response shaping only. Ownership and
task/event resolution live in the service layer, per ARCHITECTURE.md
Section 3.
"""

from rest_framework import serializers

from apps.reminders.models import Reminder


class LinkedRefSerializer(serializers.Serializer):
    """Minimal reference to a linked task or event."""

    id = serializers.UUIDField()
    title = serializers.CharField()


class ReminderSerializer(serializers.ModelSerializer):
    """Full reminder representation."""

    task = LinkedRefSerializer(read_only=True)
    event = LinkedRefSerializer(read_only=True)

    class Meta:
        model = Reminder
        fields = [
            'id',
            'title',
            'message',
            'trigger_type',
            'remind_at',
            'task',
            'event',
            'is_sent',
            'sent_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields


class ReminderWriteSerializer(serializers.Serializer):
    """Validates create/update input for a reminder."""

    title = serializers.CharField(max_length=255, trim_whitespace=True, required=False)
    message = serializers.CharField(allow_blank=True, required=False)
    remind_at = serializers.DateTimeField(required=False)
    task_id = serializers.UUIDField(required=False, allow_null=True)
    event_id = serializers.UUIDField(required=False, allow_null=True)

    def validate_title(self, value: str) -> str:
        if not value.strip():
            raise serializers.ValidationError('Title cannot be blank.')
        return value.strip()

    def validate(self, attrs: dict) -> dict:
        if not self.partial:
            required_fields = ['title', 'remind_at']
            missing = [field for field in required_fields if field not in attrs]
            if missing:
                raise serializers.ValidationError(
                    {field: 'This field is required.' for field in missing}
                )
        return attrs


class ReminderFilterSerializer(serializers.Serializer):
    """Validates query parameters on GET /api/v1/reminders/."""

    is_sent = serializers.BooleanField(required=False)
    before = serializers.DateTimeField(required=False)
    after = serializers.DateTimeField(required=False)
    task_id = serializers.UUIDField(required=False)
    event_id = serializers.UUIDField(required=False)
