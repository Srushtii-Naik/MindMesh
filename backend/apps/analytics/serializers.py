"""
DRF serializers — Analytics & Insights.

Handle response shaping only. Per ARCHITECTURE.md Section 3, business logic
and aggregation live in the service layer, not here. Productivity/habit
data is assembled as plain dicts by apps.analytics.services, so these
serializers describe that shape rather than a Django model, except for
ProgressReport which is a real model.
"""

from rest_framework import serializers

from apps.analytics.models import ProgressReport

# --------------------------------------------------------------------------
# Productivity analytics
# --------------------------------------------------------------------------


class DailySeriesPointSerializer(serializers.Serializer):
    date = serializers.DateField()
    tasks_completed = serializers.IntegerField()
    tasks_created = serializers.IntegerField()


class ProductivityAnalyticsSerializer(serializers.Serializer):
    period_start = serializers.DateField()
    period_end = serializers.DateField()
    tasks_created = serializers.IntegerField()
    tasks_completed = serializers.IntegerField()
    completion_rate = serializers.FloatField()
    notes_created = serializers.IntegerField()
    events_scheduled = serializers.IntegerField()
    daily_series = DailySeriesPointSerializer(many=True)


# --------------------------------------------------------------------------
# Habit tracking
# --------------------------------------------------------------------------


class DailyActivityPointSerializer(serializers.Serializer):
    date = serializers.DateField()
    is_active_day = serializers.BooleanField()


class HabitTrackingSerializer(serializers.Serializer):
    period_start = serializers.DateField()
    period_end = serializers.DateField()
    current_streak_days = serializers.IntegerField()
    longest_streak_days = serializers.IntegerField()
    daily_activity = DailyActivityPointSerializer(many=True)


# --------------------------------------------------------------------------
# AI recommendations
# --------------------------------------------------------------------------


class RecommendationsSerializer(serializers.Serializer):
    recommendations = serializers.ListField(child=serializers.CharField())


# --------------------------------------------------------------------------
# Progress reports
# --------------------------------------------------------------------------


class ProgressReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgressReport
        fields = [
            'id',
            'period_start',
            'period_end',
            'tasks_created',
            'tasks_completed',
            'completion_rate',
            'notes_created',
            'events_scheduled',
            'current_streak_days',
            'longest_streak_days',
            'ai_summary',
            'created_at',
        ]
        read_only_fields = fields


# --------------------------------------------------------------------------
# Query params
# --------------------------------------------------------------------------


class WindowQuerySerializer(serializers.Serializer):
    """Validates the optional `?days=` query param shared by the
    productivity and habit-tracking endpoints."""

    days = serializers.IntegerField(required=False, min_value=1, max_value=365)
