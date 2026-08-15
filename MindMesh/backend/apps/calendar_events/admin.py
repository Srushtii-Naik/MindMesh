"""Django admin registration for the calendar_events app's models."""

from django.contrib import admin

from apps.calendar_events.models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'start_time', 'end_time', 'all_day', 'is_active']
    list_filter = ['all_day', 'is_active']
    search_fields = ['title', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
