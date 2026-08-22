"""Django admin registration for the tasks app's models."""

from django.contrib import admin

from apps.tasks.models import Category, SubTask, Task


class SubTaskInline(admin.TabularInline):
    model = SubTask
    extra = 0
    fields = ['title', 'is_completed', 'order', 'is_active']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'user', 'priority', 'due_date', 'is_completed', 'recurrence', 'is_active',
    ]
    list_filter = ['priority', 'recurrence', 'is_completed', 'is_active']
    search_fields = ['title', 'user__email']
    inlines = [SubTaskInline]
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'color', 'created_at']
    search_fields = ['name', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
