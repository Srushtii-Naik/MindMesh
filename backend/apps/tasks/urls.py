"""
URL routes — Tasks.

Mounted at /api/v1/tasks/ from config/urls.py, per ARCHITECTURE.md Section 6
API versioning convention.
"""

from django.urls import path

from apps.tasks.views import (
    CategoryDetailView,
    CategoryListCreateView,
    SubTaskDetailView,
    SubTaskListCreateView,
    TaskCompleteView,
    TaskDetailView,
    TaskListCreateView,
    TaskReopenView,
    TaskSuggestionsView,
    TodaySummaryView,
)

urlpatterns = [
    # Categories
    path('categories/', CategoryListCreateView.as_view(), name='task-category-list'),
    path('categories/<uuid:category_id>/', CategoryDetailView.as_view(), name='task-category-detail'),

    # Smart suggestions & dashboard summary
    path('suggestions/', TaskSuggestionsView.as_view(), name='task-suggestions'),
    path('summary/today/', TodaySummaryView.as_view(), name='task-today-summary'),

    # Tasks
    path('', TaskListCreateView.as_view(), name='task-list'),
    path('<uuid:task_id>/', TaskDetailView.as_view(), name='task-detail'),
    path('<uuid:task_id>/complete/', TaskCompleteView.as_view(), name='task-complete'),
    path('<uuid:task_id>/reopen/', TaskReopenView.as_view(), name='task-reopen'),

    # Subtasks
    path('<uuid:task_id>/subtasks/', SubTaskListCreateView.as_view(), name='subtask-list'),
    path(
        '<uuid:task_id>/subtasks/<uuid:subtask_id>/',
        SubTaskDetailView.as_view(),
        name='subtask-detail',
    ),
]
