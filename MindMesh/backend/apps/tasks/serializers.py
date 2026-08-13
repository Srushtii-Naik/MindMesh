"""
DRF serializers — Tasks.

Handle request parsing/validation and response shaping only. Per
ARCHITECTURE.md Section 3, uniqueness enforcement, ownership checks, and
recurrence logic live in the service layer, not here.
"""

from rest_framework import serializers

from apps.tasks.models import Category, Priority, RecurrenceRule, SubTask, Task


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'color', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class CategoryWriteSerializer(serializers.Serializer):
    """Validates create/update input for a category."""

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


class SubTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTask
        fields = ['id', 'title', 'is_completed', 'order', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class SubTaskWriteSerializer(serializers.Serializer):
    """Validates create/update input for a subtask."""

    title = serializers.CharField(max_length=255, trim_whitespace=True, required=False)
    is_completed = serializers.BooleanField(required=False)
    order = serializers.IntegerField(required=False, min_value=0)

    def validate_title(self, value: str) -> str:
        if not value.strip():
            raise serializers.ValidationError('Subtask title cannot be blank.')
        return value.strip()

    def validate(self, attrs: dict) -> dict:
        if not self.partial and 'title' not in attrs:
            raise serializers.ValidationError({'title': 'This field is required.'})
        return attrs


class TaskSerializer(serializers.ModelSerializer):
    """Full task representation, including nested subtasks and category."""

    category = CategorySerializer(read_only=True)
    subtasks = SubTaskSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'description',
            'category',
            'priority',
            'due_date',
            'is_completed',
            'completed_at',
            'recurrence',
            'recurrence_interval',
            'subtasks',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields


class TaskWriteSerializer(serializers.Serializer):
    """Validates create/update input for a task. `is_completed` is deliberately
    excluded — completion goes through the dedicated complete/reopen actions
    so the recurrence side-effect (see services.py) always fires consistently."""

    title = serializers.CharField(max_length=255, trim_whitespace=True, required=False)
    description = serializers.CharField(allow_blank=True, required=False)
    category_id = serializers.UUIDField(required=False, allow_null=True)
    priority = serializers.ChoiceField(choices=Priority.choices, required=False)
    due_date = serializers.DateField(required=False, allow_null=True)
    recurrence = serializers.ChoiceField(choices=RecurrenceRule.choices, required=False)
    recurrence_interval = serializers.IntegerField(required=False, min_value=1)

    def validate_title(self, value: str) -> str:
        if not value.strip():
            raise serializers.ValidationError('Title cannot be blank.')
        return value.strip()

    def validate(self, attrs: dict) -> dict:
        if not self.partial and 'title' not in attrs:
            raise serializers.ValidationError({'title': 'This field is required.'})
        return attrs


class TaskFilterSerializer(serializers.Serializer):
    """
    Validates query parameters on GET /api/v1/tasks/.

    `is_completed` is deliberately NOT a BooleanField here: DRF treats
    QueryDicts as HTML form input, so BooleanField.get_value() returns
    False for a *missing* key (mirroring an unchecked HTML checkbox) rather
    than leaving it absent — which would silently filter every list request
    down to open tasks only. It's parsed manually instead; see views.py.
    """

    priority = serializers.ChoiceField(choices=Priority.choices, required=False)
    category_id = serializers.UUIDField(required=False)
    due_before = serializers.DateField(required=False)
    due_after = serializers.DateField(required=False)
    search = serializers.CharField(required=False, allow_blank=False)


class TaskSuggestionSerializer(serializers.Serializer):
    id = serializers.CharField()
    kind = serializers.CharField()
    message = serializers.CharField()
    task_id = serializers.CharField(allow_null=True)


class TodaySummarySerializer(serializers.Serializer):
    due_today_count = serializers.IntegerField()
    overdue_count = serializers.IntegerField()
    completed_today_count = serializers.IntegerField()
