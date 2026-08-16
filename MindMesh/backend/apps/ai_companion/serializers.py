"""
DRF serializers — AI Companion.

Handle request parsing/validation and response shaping only. Per
ARCHITECTURE.md Section 3, ownership checks and business logic live in the
service layer, not here.
"""

from rest_framework import serializers

from apps.ai_companion.models import Conversation, MemoryFact, Message

# --------------------------------------------------------------------------
# Conversations
# --------------------------------------------------------------------------


class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ['id', 'title', 'created_at', 'updated_at']
        read_only_fields = fields


class ConversationWriteSerializer(serializers.Serializer):
    """Validates create input for a conversation. `title` is optional — the
    service layer derives one from the first message if omitted."""

    title = serializers.CharField(max_length=255, required=False, allow_blank=True, default='')


# --------------------------------------------------------------------------
# Messages
# --------------------------------------------------------------------------


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'role', 'content', 'created_at']
        read_only_fields = fields


class MessageWriteSerializer(serializers.Serializer):
    """Validates the content of an outgoing chat message."""

    content = serializers.CharField(trim_whitespace=True)

    def validate_content(self, value: str) -> str:
        if not value.strip():
            raise serializers.ValidationError('Message content cannot be blank.')
        return value.strip()


# --------------------------------------------------------------------------
# Memory
# --------------------------------------------------------------------------


class MemoryFactSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemoryFact
        fields = ['id', 'fact_text', 'created_at']
        read_only_fields = fields


# --------------------------------------------------------------------------
# AI-enhanced suggestions — mirrors apps.tasks.serializers.TaskSuggestionSerializer's
# shape exactly (dict-backed, not a model), since the payload is the same
# suggestion structure extended with one AI-generated entry.
# --------------------------------------------------------------------------


class AISuggestionSerializer(serializers.Serializer):
    id = serializers.CharField()
    kind = serializers.CharField()
    message = serializers.CharField()
    task_id = serializers.CharField(allow_null=True)
