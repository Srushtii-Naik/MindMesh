"""
Repository / data-access layer — Tasks.

Encapsulates ORM queries for Task, SubTask, and Category, isolating
persistence details from the service layer, per ARCHITECTURE.md Section 3.
Every query here is scoped to a given user — row-level ownership per
PROJECT_RULES.md Section 7.
"""

from datetime import date

from django.db.models import QuerySet
from django.utils import timezone

from apps.accounts.models import User
from apps.tasks.models import Category, SubTask, Task

# --------------------------------------------------------------------------
# Category
# --------------------------------------------------------------------------


def list_categories_for_user(user: User) -> QuerySet[Category]:
    return Category.objects.filter(user=user)


def get_category_for_user(user: User, category_id) -> Category | None:
    return Category.objects.filter(user=user, id=category_id).first()


def create_category(*, user: User, name: str, color: str) -> Category:
    return Category.objects.create(user=user, name=name, color=color)


def update_category(category: Category, **fields) -> Category:
    for field, value in fields.items():
        setattr(category, field, value)
    category.save()
    return category


def delete_category(category: Category) -> None:
    category.delete()


def category_name_exists_for_user(user: User, name: str, *, exclude_id=None) -> bool:
    qs = Category.objects.filter(user=user, name__iexact=name)
    if exclude_id is not None:
        qs = qs.exclude(id=exclude_id)
    return qs.exists()


# --------------------------------------------------------------------------
# Task
# --------------------------------------------------------------------------


def list_tasks_for_user(user: User) -> QuerySet[Task]:
    """Base queryset of the user's non-deleted tasks. Filters applied by the service layer."""
    return Task.objects.filter(user=user, is_active=True).select_related('category')


def get_task_for_user(user: User, task_id) -> Task | None:
    return Task.objects.filter(user=user, id=task_id, is_active=True).select_related('category').first()


def create_task(*, user: User, **fields) -> Task:
    return Task.objects.create(user=user, **fields)


def update_task(task: Task, **fields) -> Task:
    for field, value in fields.items():
        setattr(task, field, value)
    task.save()
    return task


def soft_delete_task(task: Task) -> None:
    task.is_active = False
    task.deleted_at = timezone.now()
    task.save(update_fields=['is_active', 'deleted_at', 'updated_at'])


def count_tasks_due_on(user: User, target_date: date) -> int:
    return Task.objects.filter(
        user=user, is_active=True, is_completed=False, due_date=target_date
    ).count()


def count_tasks_overdue(user: User, as_of: date) -> int:
    return Task.objects.filter(
        user=user, is_active=True, is_completed=False, due_date__lt=as_of
    ).count()


def count_tasks_completed_on(user: User, target_date: date) -> int:
    return Task.objects.filter(
        user=user, is_active=True, is_completed=True, completed_at__date=target_date
    ).count()


def list_tasks_due_between(user: User, start_date: date, end_date: date) -> QuerySet[Task]:
    """Tasks with a due_date inside [start_date, end_date] (ROADMAP.md Milestone 5 —
    calendar integration). Recurring tasks generate a new Task row per occurrence
    (see generate_next_occurrence in services.py), so this naturally picks up every
    occurrence whose due_date falls in range."""
    return list_tasks_for_user(user).filter(due_date__gte=start_date, due_date__lte=end_date)


# --------------------------------------------------------------------------
# SubTask
# --------------------------------------------------------------------------


def list_subtasks_for_task(task: Task) -> QuerySet[SubTask]:
    return SubTask.objects.filter(task=task, is_active=True)


def get_subtask_for_task(task: Task, subtask_id) -> SubTask | None:
    return SubTask.objects.filter(task=task, id=subtask_id, is_active=True).first()


def create_subtask(*, task: Task, **fields) -> SubTask:
    return SubTask.objects.create(task=task, **fields)


def update_subtask(subtask: SubTask, **fields) -> SubTask:
    for field, value in fields.items():
        setattr(subtask, field, value)
    subtask.save()
    return subtask


def soft_delete_subtask(subtask: SubTask) -> None:
    subtask.is_active = False
    subtask.deleted_at = timezone.now()
    subtask.save(update_fields=['is_active', 'deleted_at', 'updated_at'])
