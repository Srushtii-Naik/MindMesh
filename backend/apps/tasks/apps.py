from django.apps import AppConfig


class TasksConfig(AppConfig):
    """
    tasks domain app.

    Implements ROADMAP.md Milestone 4 (Task Management): tasks, subtasks,
    categories, priorities, due dates, recurrence, and rule-based smart
    suggestions.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.tasks'
