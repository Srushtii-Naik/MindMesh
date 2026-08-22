"""
DRF views — Tasks.

Handles HTTP concerns only (request parsing, status codes, response
shaping, pagination). Business logic is delegated to apps.tasks.services,
per ARCHITECTURE.md Section 3.
"""

from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.tasks.serializers import (
    CategorySerializer,
    CategoryWriteSerializer,
    SubTaskSerializer,
    SubTaskWriteSerializer,
    TaskFilterSerializer,
    TaskSerializer,
    TaskSuggestionSerializer,
    TaskWriteSerializer,
    TodaySummarySerializer,
)
from apps.tasks.services import (
    CategoryNameAlreadyExistsError,
    CategoryNotFoundError,
    SubtaskNotFoundError,
    TaskNotFoundError,
    complete_task_for_user,
    create_category_for_user,
    create_subtask_for_user_task,
    create_task_for_user,
    delete_category_for_user,
    delete_subtask_for_user_task,
    delete_task_for_user,
    get_category,
    get_task,
    get_task_suggestions,
    get_today_summary,
    list_categories,
    list_subtasks_for_user_task,
    list_tasks_for_user_filtered,
    reopen_task_for_user,
    update_category_for_user,
    update_subtask_for_user_task,
    update_task_for_user,
)


# --------------------------------------------------------------------------
# Categories
# --------------------------------------------------------------------------


class CategoryListCreateView(APIView):
    """
    GET  /api/v1/tasks/categories/ — list the user's categories.
    POST /api/v1/tasks/categories/ — create a category.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        categories = list_categories(request.user)
        return Response(CategorySerializer(categories, many=True).data)

    def post(self, request: Request) -> Response:
        serializer = CategoryWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            category = create_category_for_user(request.user, **serializer.validated_data)
        except CategoryNameAlreadyExistsError as exc:
            return Response(
                {'detail': str(exc), 'code': 'category_name_exists'},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(CategorySerializer(category).data, status=status.HTTP_201_CREATED)


class CategoryDetailView(APIView):
    """
    GET    /api/v1/tasks/categories/<id>/ — retrieve a category.
    PATCH  /api/v1/tasks/categories/<id>/ — update a category.
    DELETE /api/v1/tasks/categories/<id>/ — delete a category.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, category_id) -> Response:
        try:
            category = get_category(request.user, category_id)
        except CategoryNotFoundError as exc:
            return Response(
                {'detail': str(exc), 'code': 'category_not_found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(CategorySerializer(category).data)

    def patch(self, request: Request, category_id) -> Response:
        serializer = CategoryWriteSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            category = update_category_for_user(
                request.user, category_id, **serializer.validated_data
            )
        except CategoryNotFoundError as exc:
            return Response(
                {'detail': str(exc), 'code': 'category_not_found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        except CategoryNameAlreadyExistsError as exc:
            return Response(
                {'detail': str(exc), 'code': 'category_name_exists'},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(CategorySerializer(category).data)

    def delete(self, request: Request, category_id) -> Response:
        try:
            delete_category_for_user(request.user, category_id)
        except CategoryNotFoundError as exc:
            return Response(
                {'detail': str(exc), 'code': 'category_not_found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


# --------------------------------------------------------------------------
# Tasks
# --------------------------------------------------------------------------


class TaskListCreateView(APIView):
    """
    GET  /api/v1/tasks/ — list the user's tasks, filterable by
         priority/category_id/is_completed/due_before/due_after/search
         (ROADMAP.md Milestone 4: "functional and filterable").
    POST /api/v1/tasks/ — create a task.
    """

    permission_classes = [IsAuthenticated]

    pagination_class = PageNumberPagination

    def get(self, request: Request) -> Response:
        filters = TaskFilterSerializer(data=request.query_params)
        filters.is_valid(raise_exception=True)
        filter_kwargs = dict(filters.validated_data)

        # See TaskFilterSerializer docstring for why this isn't a BooleanField.
        is_completed_param = request.query_params.get('is_completed')
        if is_completed_param is not None:
            if is_completed_param.lower() not in ('true', 'false'):
                return Response(
                    {'detail': 'is_completed must be true or false.', 'code': 'invalid_filter'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            filter_kwargs['is_completed'] = is_completed_param.lower() == 'true'

        queryset = list_tasks_for_user_filtered(request.user, **filter_kwargs)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = TaskSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request: Request) -> Response:
        serializer = TaskWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            task = create_task_for_user(request.user, **serializer.validated_data)
        except CategoryNotFoundError as exc:
            return Response(
                {'detail': str(exc), 'code': 'category_not_found'},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(TaskSerializer(task).data, status=status.HTTP_201_CREATED)


class TaskDetailView(APIView):
    """
    GET    /api/v1/tasks/<id>/ — retrieve a task (with its subtasks).
    PATCH  /api/v1/tasks/<id>/ — update a task's editable fields.
    DELETE /api/v1/tasks/<id>/ — soft-delete a task.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, task_id) -> Response:
        try:
            task = get_task(request.user, task_id)
        except TaskNotFoundError as exc:
            return Response(
                {'detail': str(exc), 'code': 'task_not_found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(TaskSerializer(task).data)

    def patch(self, request: Request, task_id) -> Response:
        serializer = TaskWriteSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            task = update_task_for_user(request.user, task_id, **serializer.validated_data)
        except TaskNotFoundError as exc:
            return Response(
                {'detail': str(exc), 'code': 'task_not_found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        except CategoryNotFoundError as exc:
            return Response(
                {'detail': str(exc), 'code': 'category_not_found'},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(TaskSerializer(task).data)

    def delete(self, request: Request, task_id) -> Response:
        try:
            delete_task_for_user(request.user, task_id)
        except TaskNotFoundError as exc:
            return Response(
                {'detail': str(exc), 'code': 'task_not_found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class TaskCompleteView(APIView):
    """POST /api/v1/tasks/<id>/complete/ — mark a task complete; generates
    the next occurrence if the task recurs (services.py)."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request, task_id) -> Response:
        try:
            task = complete_task_for_user(request.user, task_id)
        except TaskNotFoundError as exc:
            return Response(
                {'detail': str(exc), 'code': 'task_not_found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(TaskSerializer(task).data)


class TaskReopenView(APIView):
    """POST /api/v1/tasks/<id>/reopen/ — undo completion."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request, task_id) -> Response:
        try:
            task = reopen_task_for_user(request.user, task_id)
        except TaskNotFoundError as exc:
            return Response(
                {'detail': str(exc), 'code': 'task_not_found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(TaskSerializer(task).data)


# --------------------------------------------------------------------------
# Subtasks
# --------------------------------------------------------------------------


class SubTaskListCreateView(APIView):
    """
    GET  /api/v1/tasks/<task_id>/subtasks/ — list a task's subtasks.
    POST /api/v1/tasks/<task_id>/subtasks/ — add a subtask.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, task_id) -> Response:
        try:
            subtasks = list_subtasks_for_user_task(request.user, task_id)
        except TaskNotFoundError as exc:
            return Response(
                {'detail': str(exc), 'code': 'task_not_found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(SubTaskSerializer(subtasks, many=True).data)

    def post(self, request: Request, task_id) -> Response:
        serializer = SubTaskWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            subtask = create_subtask_for_user_task(
                request.user, task_id, **serializer.validated_data
            )
        except TaskNotFoundError as exc:
            return Response(
                {'detail': str(exc), 'code': 'task_not_found'},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(SubTaskSerializer(subtask).data, status=status.HTTP_201_CREATED)


class SubTaskDetailView(APIView):
    """
    PATCH  /api/v1/tasks/<task_id>/subtasks/<subtask_id>/ — update a subtask.
    DELETE /api/v1/tasks/<task_id>/subtasks/<subtask_id>/ — remove a subtask.
    """

    permission_classes = [IsAuthenticated]

    def patch(self, request: Request, task_id, subtask_id) -> Response:
        serializer = SubTaskWriteSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            subtask = update_subtask_for_user_task(
                request.user, task_id, subtask_id, **serializer.validated_data
            )
        except (TaskNotFoundError, SubtaskNotFoundError) as exc:
            return Response(
                {'detail': str(exc), 'code': 'not_found'},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(SubTaskSerializer(subtask).data)

    def delete(self, request: Request, task_id, subtask_id) -> Response:
        try:
            delete_subtask_for_user_task(request.user, task_id, subtask_id)
        except (TaskNotFoundError, SubtaskNotFoundError) as exc:
            return Response(
                {'detail': str(exc), 'code': 'not_found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


# --------------------------------------------------------------------------
# Smart suggestions & dashboard summary
# --------------------------------------------------------------------------


class TaskSuggestionsView(APIView):
    """GET /api/v1/tasks/suggestions/ — rule-based smart suggestions (services.py)."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        suggestions = get_task_suggestions(request.user)
        return Response(TaskSuggestionSerializer(suggestions, many=True).data)


class TodaySummaryView(APIView):
    """GET /api/v1/tasks/summary/today/ — powers the dashboard's Today's Summary card."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        summary = get_today_summary(request.user)
        return Response(TodaySummarySerializer(summary).data)
