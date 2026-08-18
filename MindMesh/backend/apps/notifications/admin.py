"""Django admin registration for the notifications app's models."""

from django.contrib import admin

from apps.notifications.models import DeviceToken, Notification, NotificationDelivery


class NotificationDeliveryInline(admin.TabularInline):
    model = NotificationDelivery
    extra = 0
    readonly_fields = ['channel', 'status', 'error_message', 'sent_at', 'created_at']
    can_delete = False


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'notification_type', 'is_read', 'is_active', 'created_at']
    list_filter = ['notification_type', 'is_read', 'is_active']
    search_fields = ['title', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [NotificationDeliveryInline]


@admin.register(DeviceToken)
class DeviceTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'platform', 'is_active', 'created_at']
    list_filter = ['platform', 'is_active']
    search_fields = ['user__email', 'token']
    readonly_fields = ['created_at', 'updated_at']
