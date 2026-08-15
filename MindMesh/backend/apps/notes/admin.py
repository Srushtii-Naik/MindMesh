"""Django admin registration for the notes app's models."""

from django.contrib import admin

from apps.notes.models import Attachment, Category, Note, Tag


class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 0
    fields = ['original_filename', 'content_type', 'size_bytes', 'created_at']
    readonly_fields = ['created_at']


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'category', 'ai_summary_generated_at', 'is_active']
    list_filter = ['is_active', 'category']
    search_fields = ['title', 'content', 'user__email']
    filter_horizontal = ['tags']
    inlines = [AttachmentInline]
    readonly_fields = ['created_at', 'updated_at', 'ai_summary_generated_at']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'color', 'created_at']
    search_fields = ['name', 'user__email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'created_at']
    search_fields = ['name', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
