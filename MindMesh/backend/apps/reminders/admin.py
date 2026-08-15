"""Django admin registration for the reminders app's models."""

from django.contrib import admin

from apps.reminders.models import Reminder


@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'remind_at', 'is_sent', 'is_active']
    list_filter = ['is_sent', 'is_active', 'trigger_type']
    search_fields = ['title', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
