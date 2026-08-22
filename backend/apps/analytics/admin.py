"""Django admin registration for the analytics app's models."""

from django.contrib import admin

from apps.analytics.models import ProgressReport


@admin.register(ProgressReport)
class ProgressReportAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'period_start', 'period_end', 'tasks_completed', 'completion_rate',
        'current_streak_days', 'created_at',
    ]
    list_filter = ['period_start', 'period_end']
    search_fields = ['user__email']
    readonly_fields = ['created_at', 'updated_at']
