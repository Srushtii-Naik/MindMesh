"""
DRF serializers — Notes.

Handle request parsing/validation and response shaping only. Per
ARCHITECTURE.md Section 3, uniqueness enforcement, ownership checks, and
search logic live in the service layer, not here.
"""

from rest_framework import serializers

from apps.notes.models import Attachment, Category, Note, Tag

# --------------------------------------------------------------------------
# Categories
# --------------------------------------------------------------------------


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'color', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class CategoryWriteSerializer(serializers.Serializer):
    """Validates create/update input for a note category."""

    name = serializers.CharField(max_length=100, trim_whitespace=True)
    color = serializers.RegexField(
        regex=r'^#[0-9A-Fa-f]{6}$',
        required=False,
        default='#5f6dfa',
        error_messages={'invalid': 'Color must be a hex value like #5f6dfa.'},
    )

    def validate_name(self, value: str) -> str:
        if not value.strip():
            raise serializers.ValidationError('Category name cannot be blank.')
        return value.strip()


# --------------------------------------------------------------------------
# Tags
# --------------------------------------------------------------------------


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class TagWriteSerializer(serializers.Serializer):
    """Validates create input for a note tag."""

    name = serializers.CharField(max_length=50, trim_whitespace=True)

    def validate_name(self, value: str) -> str:
        if not value.strip():
            raise serializers.ValidationError('Tag name cannot be blank.')
        return value.strip()


# --------------------------------------------------------------------------
# Attachments
# --------------------------------------------------------------------------


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ['id', 'original_filename', 'content_type', 'size_bytes', 'created_at']
        read_only_fields = fields


# --------------------------------------------------------------------------
# Notes
# --------------------------------------------------------------------------


class NoteSerializer(serializers.ModelSerializer):
    """Full note representation, including nested category, tags, and attachments."""

    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = Note
        fields = [
            'id',
            'title',
            'content',
            'category',
            'tags',
            'attachments',
            'ai_summary',
            'ai_summary_generated_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields


class NoteWriteSerializer(serializers.Serializer):
    """Validates create/update input for a note."""

    title = serializers.CharField(max_length=255, trim_whitespace=True, required=False)
    content = serializers.CharField(allow_blank=True, required=False)
    category_id = serializers.UUIDField(required=False, allow_null=True)
    tag_ids = serializers.ListField(
        child=serializers.UUIDField(), required=False, allow_empty=True
    )

    def validate_title(self, value: str) -> str:
        if not value.strip():
            raise serializers.ValidationError('Title cannot be blank.')
        return value.strip()

    def validate(self, attrs: dict) -> dict:
        if not self.partial and 'title' not in attrs:
            raise serializers.ValidationError({'title': 'This field is required.'})
        return attrs


class NoteFilterSerializer(serializers.Serializer):
    """Validates query parameters on GET /api/v1/notes/."""

    category_id = serializers.UUIDField(required=False)
    tag_id = serializers.UUIDField(required=False)
    search = serializers.CharField(required=False, allow_blank=False)
