"""Django admin registration for the family app's models."""

from django.contrib import admin

from apps.family.models import (
    EmergencyContact,
    Family,
    FamilyInvitation,
    FamilyMembership,
    SharedResource,
)


class FamilyMembershipInline(admin.TabularInline):
    model = FamilyMembership
    extra = 0
    readonly_fields = ['created_at', 'removed_at']


@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'created_by__email']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [FamilyMembershipInline]


@admin.register(FamilyInvitation)
class FamilyInvitationAdmin(admin.ModelAdmin):
    list_display = ['invited_email', 'family', 'role', 'status', 'expires_at', 'created_at']
    list_filter = ['status', 'role']
    search_fields = ['invited_email', 'family__name']
    readonly_fields = ['token', 'created_at', 'updated_at']


@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'family', 'phone_number', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'family__name', 'phone_number']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(SharedResource)
class SharedResourceAdmin(admin.ModelAdmin):
    list_display = ['resource_type', 'resource_id', 'family', 'owner', 'can_edit', 'is_active']
    list_filter = ['resource_type', 'can_edit', 'is_active']
    search_fields = ['family__name', 'owner__email']
    readonly_fields = ['created_at', 'updated_at']
