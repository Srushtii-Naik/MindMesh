"""
Domain models — Tasks.

Per ARCHITECTURE.md Section 4: every domain table is scoped to a user_id
with row-level ownership enforced at the service layer, and timestamps are
standardized across all tables. Per PROJECT_RULES.md Section 7, Task and
SubTask (user-generated content) use soft deletes; Category is a lightweight
tag rather than content in its own right, so it's hard-deleted with tasks
falling back to "uncategorized" via SET_NULL — documented on the field.
"""

import uuid

from django.conf import settings
from django.db import models


class Priority(models.TextChoices):
    LOW = 'low', 'Low'
    MEDIUM = 'medium', 'Medium'
    HIGH = 'high', 'High'
    URGENT = 'urgent', 'Urgent'


class RecurrenceRule(models.TextChoices):
    """Rule-based recurrence per ROADMAP.md Milestone 4 ("Recurring tasks")."""

    NONE = 'none', 'Does not repeat'
    DAILY = 'daily', 'Daily'
    WEEKLY = 'weekly', 'Weekly'
    MONTHLY = 'monthly', 'Monthly'


class Category(models.Model):
    """
    A user-defined label for grouping tasks (ROADMAP.md Milestone 4:
    "Categories"). Deliberately simple — name and a display color — since
    it's a tag, not content that itself needs a soft-delete/recovery story.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='task_categories'
    )
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#5f6dfa')  # brand-500

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tasks_category'
        ordering = ['name']
        verbose_name = 'category'
        verbose_name_plural = 'categories'
        constraints = [
            models.UniqueConstraint(fields=['user', 'name'], name='unique_category_name_per_user')
        ]

    def __str__(self) -> str:
        return self.name


class Task(models.Model):
    """
    A single task owned by a user.

    `recurrence`/`recurrence_interval` describe how this task repeats;
    completing a recurring task generates the next occurrence as a new Task
    row (see apps/tasks/services.py `generate_next_occurrence`) rather than
    mutating this one, so completed occurrences remain in history.
    `recurrence_parent` links an occurrence back to the task it was
    generated from, for that history.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tasks'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks',
    )
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    due_date = models.DateField(null=True, blank=True)

    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    recurrence = models.CharField(
        max_length=10, choices=RecurrenceRule.choices, default=RecurrenceRule.NONE
    )
    recurrence_interval = models.PositiveIntegerField(default=1)
    recurrence_parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recurrence_children',
    )

    # Soft delete (PROJECT_RULES.md Section 7).
    is_active = models.BooleanField(default=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tasks_task'
        ordering = ['-created_at']
        verbose_name = 'task'
        verbose_name_plural = 'tasks'
        indexes = [
            models.Index(fields=['user', 'is_active', 'is_completed']),
            models.Index(fields=['user', 'due_date']),
        ]

    def __str__(self) -> str:
        return self.title


class SubTask(models.Model):
    """A small, ordered checklist item belonging to a Task."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='subtasks')
    title = models.CharField(max_length=255)
    is_completed = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    # Soft delete (PROJECT_RULES.md Section 7).
    is_active = models.BooleanField(default=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tasks_subtask'
        ordering = ['order', 'created_at']
        verbose_name = 'subtask'
        verbose_name_plural = 'subtasks'

    def __str__(self) -> str:
        return self.title
