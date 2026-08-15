"""
DRF views — Reminders.

Handles HTTP concerns only. Business logic is delegated to
apps.reminders.services, per ARCHITECTURE.md Section 3.
"""

from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.reminders.serializers import (
    ReminderFilterSerializer,
    ReminderSerializer,
    ReminderWriteSerializer,
)
from apps.reminders.services import (
    LinkedEventNotFoundError,
    LinkedTaskNotFoundError,
    ReminderNotFoundError,
    create_reminder_for_user,
    delete_reminder_for_user,
    get_reminder,
    list_reminders_for_user_filtered,
    update_reminder_for_user,
)


class ReminderListCreateView(APIView):
    """
    GET  /api/v1/reminders/ — list the user's reminders, filterable by
         is_sent/before/after/task_id/event_id.
    POST /api/v1/reminders/ — create a reminder (data model only; delivery
         is deferred to Milestone 9 per ROADMAP.md).
    """

    permission_classes = [IsAuthenticated]

    pagination_class = PageNumberPagination

    def get(self, request: Request) -> Response:
        filters = ReminderFilterSerializer(data=request.query_params)
        filters.is_valid(raise_exception=True)

        queryset = list_reminders_for_user_filtered(request.user, **filters.validated_data)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = ReminderSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request: Request) -> Response:
        serializer = ReminderWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            reminder = create_reminder_for_user(request.user, **serializer.validated_data)
        except LinkedTaskNotFoundError as exc:
            return Response(
                {'detail': str(exc), 'code': 'task_not_found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        except LinkedEventNotFoundError as exc:
            return Response(
                {'detail': str(exc), 'code': 'event_not_found'},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(ReminderSerializer(reminder).data, status=status.HTTP_201_CREATED)


class ReminderDetailView(APIView):
    """
    GET    /api/v1/reminders/<id>/ — retrieve a reminder.
    PATCH  /api/v1/reminders/<id>/ — update a reminder's editable fields.
    DELETE /api/v1/reminders/<id>/ — soft-delete a reminder.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, reminder_id) -> Response:
        try:
            reminder = get_reminder(request.user, reminder_id)
        except ReminderNotFoundError as exc:
            return Response(
                {'detail': str(exc), 'code': 'reminder_not_found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(ReminderSerializer(reminder).data)

    def patch(self, request: Request, reminder_id) -> Response:
        serializer = ReminderWriteSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            reminder = update_reminder_for_user(
                request.user, reminder_id, **serializer.validated_data
            )
        except ReminderNotFoundError as exc:
            return Response(
                {'detail': str(exc), 'code': 'reminder_not_found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        except LinkedTaskNotFoundError as exc:
            return Response(
                {'detail': str(exc), 'code': 'task_not_found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        except LinkedEventNotFoundError as exc:
            return Response(
                {'detail': str(exc), 'code': 'event_not_found'},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(ReminderSerializer(reminder).data)

    def delete(self, request: Request, reminder_id) -> Response:
        try:
            delete_reminder_for_user(request.user, reminder_id)
        except ReminderNotFoundError as exc:
            return Response(
                {'detail': str(exc), 'code': 'reminder_not_found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)
