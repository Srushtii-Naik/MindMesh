"""
Service layer — Tasks.

Domain business logic for categories, tasks, subtasks, recurrence, rule-based
suggestions, and the dashboard's "today" summary. Per ARCHITECTURE.md
Section 3: views call services; services never import DRF.
"""

import calendar
from datetime import date, timedelta

from django.utils import timezone

from apps.accounts.models import User
from apps.tasks.models import Category, Priority, RecurrenceRule, SubTask, Task
from apps.tasks.repositories import (
    category_name_exists_for_user,
    count_tasks_completed_on,
    count_tasks_due_on,
    count_tasks_overdue,
    create_category,
    create_subtask,
    create_task,
    delete_category,
    get_category_for_user,
    get_subtask_for_task,
    get_task_for_user,
    list_categories_for_user,
    list_subtasks_for_task,
    list_tasks_due_between,
    list_tasks_for_user,
    soft_delete_subtask,
    soft_delete_task,
    update_category,
    update_subtask,
    update_task,
)


class CategoryNotFoundError(Exception):
    """Raised when a category cannot be found for the requesting user."""


class CategoryNameAlreadyExistsError(Exception):
    """Raised when creating/renaming a category to a name the user already has."""


class TaskNotFoundError(Exception):
    """Raised when a task cannot be found for the requesting user."""


class SubtaskNotFoundError(Exception):
    """Raised when a subtask cannot be found under the requesting user's task."""


# --------------------------------------------------------------------------
# Categories
# --------------------------------------------------------------------------


def list_categories(user: User):
    return list_categories_for_user(user)


def create_category_for_user(user: User, *, name: str, color: str) -> Category:
    name = name.strip()
    if category_name_exists_for_user(user, name):
        raise CategoryNameAlreadyExistsError(f'You already have a category named "{name}".')
    return create_category(user=user, name=name, color=color)


def update_category_for_user(user: User, category_id, **fields) -> Category:
    category = get_category_for_user(user, category_id)
    if category is None:
        raise CategoryNotFoundError('Category not found.')

    if 'name' in fields:
        name = fields['name'].strip()
        if category_name_exists_for_user(user, name, exclude_id=category.id):
            raise CategoryNameAlreadyExistsError(f'You already have a category named "{name}".')
        fields['name'] = name

    return update_category(category, **fields)


def delete_category_for_user(user: User, category_id) -> None:
    category = get_category_for_user(user, category_id)
    if category is None:
        raise CategoryNotFoundError('Category not found.')
    delete_category(category)


# --------------------------------------------------------------------------
# Tasks
# --------------------------------------------------------------------------


def _resolve_category(user: User, category_id) -> Category | None:
    if category_id is None:
        return None
    category = get_category_for_user(user, category_id)
    if category is None:
        raise CategoryNotFoundError('Category not found.')
    return category


def get_category(user: User, category_id) -> Category:
    category = get_category_for_user(user, category_id)
    if category is None:
        raise CategoryNotFoundError('Category not found.')
    return category


def list_tasks_for_user_filtered(
    user: User,
    *,
    priority: str | None = None,
    category_id=None,
    is_completed: bool | None = None,
    due_before: date | None = None,
    due_after: date | None = None,
    search: str | None = None,
):
    """
    Filterable task listing (ROADMAP.md Milestone 4: "Priorities, due dates,
    and categories functional and filterable").
    """
    queryset = list_tasks_for_user(user)

    if priority:
        queryset = queryset.filter(priority=priority)
    if category_id:
        queryset = queryset.filter(category_id=category_id)
    if is_completed is not None:
        queryset = queryset.filter(is_completed=is_completed)
    if due_before:
        queryset = queryset.filter(due_date__lte=due_before)
    if due_after:
        queryset = queryset.filter(due_date__gte=due_after)
    if search:
        queryset = queryset.filter(title__icontains=search)

    return queryset


def create_task_for_user(
    user: User,
    *,
    title: str,
    description: str = '',
    category_id=None,
    priority: str = Priority.MEDIUM,
    due_date: date | None = None,
    recurrence: str = RecurrenceRule.NONE,
    recurrence_interval: int = 1,
) -> Task:
    category = _resolve_category(user, category_id)
    if recurrence == RecurrenceRule.NONE:
        recurrence_interval = 1

    return create_task(
        user=user,
        title=title.strip(),
        description=description,
        category=category,
        priority=priority,
        due_date=due_date,
        recurrence=recurrence,
        recurrence_interval=recurrence_interval,
    )


def update_task_for_user(user: User, task_id, **fields) -> Task:
    task = get_task_for_user(user, task_id)
    if task is None:
        raise TaskNotFoundError('Task not found.')

    if 'category_id' in fields:
        fields['category'] = _resolve_category(user, fields.pop('category_id'))
    if fields.get('recurrence') == RecurrenceRule.NONE:
        fields['recurrence_interval'] = 1
    if 'title' in fields:
        fields['title'] = fields['title'].strip()

    return update_task(task, **fields)


def delete_task_for_user(user: User, task_id) -> None:
    task = get_task_for_user(user, task_id)
    if task is None:
        raise TaskNotFoundError('Task not found.')
    soft_delete_task(task)


def get_task(user: User, task_id) -> Task:
    task = get_task_for_user(user, task_id)
    if task is None:
        raise TaskNotFoundError('Task not found.')
    return task


def _add_months(base: date, months: int) -> date:
    """Advance a date by whole calendar months, clamping the day to the target month's length."""
    month_index = base.month - 1 + months
    year = base.year + month_index // 12
    month = month_index % 12 + 1
    day = min(base.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def _advance_due_date(current: date | None, rule: str, interval: int) -> date:
    base = current or timezone.localdate()
    if rule == RecurrenceRule.DAILY:
        return base + timedelta(days=interval)
    if rule == RecurrenceRule.WEEKLY:
        return base + timedelta(weeks=interval)
    if rule == RecurrenceRule.MONTHLY:
        return _add_months(base, interval)
    return base


def generate_next_occurrence(task: Task) -> Task | None:
    """
    Create the next occurrence of a recurring task, rule-based per
    ROADMAP.md Milestone 4 ("Smart suggestions (rule-based initially,
    AI-enhanced later)" applies to suggestions; recurrence itself is
    rule-based from the start). Returns None for a non-recurring task.
    """
    if task.recurrence == RecurrenceRule.NONE:
        return None

    next_due = _advance_due_date(task.due_date, task.recurrence, task.recurrence_interval)
    return create_task(
        user=task.user,
        title=task.title,
        description=task.description,
        category=task.category,
        priority=task.priority,
        due_date=next_due,
        recurrence=task.recurrence,
        recurrence_interval=task.recurrence_interval,
        recurrence_parent=task,
    )


def complete_task_for_user(user: User, task_id) -> Task:
    """Mark a task complete, generating its next occurrence if it recurs."""
    task = get_task_for_user(user, task_id)
    if task is None:
        raise TaskNotFoundError('Task not found.')

    if not task.is_completed:
        update_task(task, is_completed=True, completed_at=timezone.now())
        generate_next_occurrence(task)

    return task


def reopen_task_for_user(user: User, task_id) -> Task:
    """Undo completion. No recurrence side effect — the next occurrence, if any, stands on its own."""
    task = get_task_for_user(user, task_id)
    if task is None:
        raise TaskNotFoundError('Task not found.')

    if task.is_completed:
        update_task(task, is_completed=False, completed_at=None)

    return task


# --------------------------------------------------------------------------
# Subtasks
# --------------------------------------------------------------------------


def _get_owned_task(user: User, task_id) -> Task:
    task = get_task_for_user(user, task_id)
    if task is None:
        raise TaskNotFoundError('Task not found.')
    return task


def list_subtasks_for_user_task(user: User, task_id):
    task = _get_owned_task(user, task_id)
    return list_subtasks_for_task(task)


def create_subtask_for_user_task(user: User, task_id, *, title: str, order: int = 0) -> SubTask:
    task = _get_owned_task(user, task_id)
    return create_subtask(task=task, title=title.strip(), order=order)


def update_subtask_for_user_task(user: User, task_id, subtask_id, **fields) -> SubTask:
    task = _get_owned_task(user, task_id)
    subtask = get_subtask_for_task(task, subtask_id)
    if subtask is None:
        raise SubtaskNotFoundError('Subtask not found.')

    if 'title' in fields:
        fields['title'] = fields['title'].strip()

    return update_subtask(subtask, **fields)


def delete_subtask_for_user_task(user: User, task_id, subtask_id) -> None:
    task = _get_owned_task(user, task_id)
    subtask = get_subtask_for_task(task, subtask_id)
    if subtask is None:
        raise SubtaskNotFoundError('Subtask not found.')
    soft_delete_subtask(subtask)


# --------------------------------------------------------------------------
# Smart suggestions (rule-based per ROADMAP.md Milestone 4; AI-enhanced in a
# later milestone once the AI abstraction layer exists — PROJECT_RULES.md
# Section 10 forbids calling an AI provider directly from here).
# --------------------------------------------------------------------------


def get_task_suggestions(user: User) -> list[dict]:
    today = timezone.localdate()
    base = list_tasks_for_user(user).filter(is_completed=False)
    suggestions: list[dict] = []

    overdue_count = base.filter(due_date__lt=today).count()
    if overdue_count:
        noun = 'task' if overdue_count == 1 else 'tasks'
        suggestions.append({
            'id': 'overdue',
            'kind': 'overdue',
            'message': (
                f'You have {overdue_count} overdue {noun}. '
                'Consider rescheduling or tackling them first.'
            ),
            'task_id': None,
        })

    due_today_count = base.filter(due_date=today).count()
    if due_today_count:
        noun = 'task' if due_today_count == 1 else 'tasks'
        suggestions.append({
            'id': 'due-today',
            'kind': 'due_today',
            'message': f'You have {due_today_count} {noun} due today.',
            'task_id': None,
        })

    undated_urgent = (
        base.filter(due_date__isnull=True, priority__in=[Priority.HIGH, Priority.URGENT])
        .order_by('-created_at')
        .first()
    )
    if undated_urgent:
        suggestions.append({
            'id': f'no-due-date-{undated_urgent.id}',
            'kind': 'missing_due_date',
            'message': f'"{undated_urgent.title}" is high priority but has no due date set.',
            'task_id': str(undated_urgent.id),
        })

    for task in base.prefetch_related('subtasks'):
        subtasks = [subtask for subtask in task.subtasks.all() if subtask.is_active]
        if subtasks and all(subtask.is_completed for subtask in subtasks):
            suggestions.append({
                'id': f'ready-{task.id}',
                'kind': 'ready_to_complete',
                'message': f'All subtasks for "{task.title}" are done — mark it complete?',
                'task_id': str(task.id),
            })
            break  # one is enough to act on; avoid flooding the UI

    return suggestions


def get_tasks_due_between(user: User, start_date: date, end_date: date):
    """Service-layer entry point for other domains (e.g. calendar_events) to read
    task due dates without importing the Task model directly, per ARCHITECTURE.md
    Section 3 ("cross-domain communication happens through service interfaces,
    not direct model imports across apps")."""
    return list_tasks_due_between(user, start_date, end_date)


def get_today_summary(user: User) -> dict:
    """Powers the dashboard's Today's Summary card (ROADMAP.md Milestone 4)."""
    today = timezone.localdate()
    return {
        'due_today_count': count_tasks_due_on(user, today),
        'overdue_count': count_tasks_overdue(user, today),
        'completed_today_count': count_tasks_completed_on(user, today),
    }
