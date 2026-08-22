"""Django admin registration for the accounts app's models."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from apps.accounts.models import User, UserSettings


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Minimal admin config — sufficient for local inspection during development."""

    ordering = ['-created_at']
    list_display = ['email', 'full_name', 'auth_provider', 'is_staff', 'is_active', 'created_at']
    list_filter = ['auth_provider', 'is_staff', 'is_active']
    search_fields = ['email', 'full_name']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('full_name',)}),
        ('OAuth', {'fields': ('auth_provider', 'google_sub')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'password1', 'password2'),
        }),
    )
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ['user', 'theme_preference', 'email_notifications_enabled', 'updated_at']
    search_fields = ['user__email']
