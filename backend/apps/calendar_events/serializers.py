"""
DRF serializers — Calendar & Scheduling.

Handle request parsing/validation and response shaping only. Per
ARCHITECTURE.md Section 3, ownership checks and range validation live in
the service layer, not here.

Task entries in calendar/planner responses reuse apps.tasks.serializers.
TaskSerializer rather than redefining a parallel shape, per PROJECT_RULES.md
Section 3 (DRY) — the frontend already knows how to render a Task, so the
same JSON shape is reused wherever a task appears on the calendar.
"""

from rest_framework import serializers

from apps.calendar_events.models import Event
from apps.tasks.serializers import TaskSerializer


class LinkedTaskSerializer(serializers.Serializer):
    """Minimal task reference nested inside an Event — enough for the UI to
    show a link without duplicating the full task payload on every event."""

    id = serializers.UUIDField()
    title = serializers.CharField()
    is_completed = serializers.BooleanField()


class EventSerializer(serializers.ModelSerializer):
    """Full event representation."""

    task = LinkedTaskSerializer(read_only=True)

    class Meta:
        model = Event
        fields = [
            'id',
            'title',
            'description',
            'location',
            'start_time',
            'end_time',
            'all_day',
            'color',
            'task',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields


class EventWriteSerializer(serializers.Serializer):
    """Validates create/update input for an event."""

    title = serializers.CharField(max_length=255, trim_whitespace=True, required=False)
    description = serializers.CharField(allow_blank=True, required=False)
    location = serializers.CharField(max_length=255, allow_blank=True, required=False)
    start_time = serializers.DateTimeField(required=False)
    end_time = serializers.DateTimeField(required=False)
    all_day = serializers.BooleanField(required=False)
    color = serializers.RegexField(
        regex=r'^#[0-9A-Fa-f]{6}$',
        required=False,
        default='#5f6dfa',
        error_messages={'invalid': 'Color must be a hex value like #5f6dfa.'},
    )
    task_id = serializers.UUIDField(required=False, allow_null=True)

    def validate_title(self, value: str) -> str:
        if not value.strip():
            raise serializers.ValidationError('Title cannot be blank.')
        return value.strip()

    def validate(self, attrs: dict) -> dict:
        if not self.partial:
            required_fields = ['title', 'start_time', 'end_time']
            missing = [field for field in required_fields if field not in attrs]
            if missing:
                raise serializers.ValidationError(
                    {field: 'This field is required.' for field in missing}
                )
        return attrs


class EventFilterSerializer(serializers.Serializer):
    """Validates query parameters on GET /api/v1/calendar/events/."""

    start = serializers.DateTimeField(required=False)
    end = serializers.DateTimeField(required=False)
    task_id = serializers.UUIDField(required=False)
    search = serializers.CharField(required=False, allow_blank=False)


class CalendarRangeSerializer(serializers.Serializer):
    """Validates the required date range on GET /api/v1/calendar/view/."""

    start = serializers.DateField()
    end = serializers.DateField()

    def validate(self, attrs: dict) -> dict:
        if attrs['end'] < attrs['start']:
            raise serializers.ValidationError({'end': 'End date must not be before start date.'})
        return attrs


class DailyPlannerQuerySerializer(serializers.Serializer):
    date = serializers.DateField()


class WeeklyPlannerQuerySerializer(serializers.Serializer):
    start = serializers.DateField()


class CalendarViewSerializer(serializers.Serializer):
    events = EventSerializer(many=True)
    tasks = TaskSerializer(many=True)


class DailyPlannerSerializer(serializers.Serializer):
    date = serializers.DateField()
    events = EventSerializer(many=True)
    tasks = TaskSerializer(many=True)


class WeeklyPlannerDaySerializer(serializers.Serializer):
    date = serializers.DateField()
    events = EventSerializer(many=True)
    tasks = TaskSerializer(many=True)


class WeeklyPlannerSerializer(serializers.Serializer):
    week_start = serializers.DateField()
    week_end = serializers.DateField()
    days = WeeklyPlannerDaySerializer(many=True)
