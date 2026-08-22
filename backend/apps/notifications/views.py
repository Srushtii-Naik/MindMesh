"""
DRF views — Notifications.

Handles HTTP concerns only. Business logic is delegated to
apps.notifications.services, per ARCHITECTURE.md Section 3.
"""

from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.notifications.serializers import (
    DeviceTokenSerializer,
    DeviceTokenWriteSerializer,
    NotificationSerializer,
    NotificationUpdateSerializer,
)
from apps.notifications.services import (
    DeviceTokenNotFoundError,
    NotificationNotFoundError,
    delete_notification_for_user,
    get_notification,
    get_unread_count_for_user,
    list_notifications_for_user_filtered,
    mark_all_notifications_read,
    register_device_token_for_user,
    unregister_device_token_for_user,
    update_notification_read_state,
)


class NotificationListView(APIView):
    """GET /api/v1/notifications/ — list the user's notifications, newest
    first, filterable by is_read/notification_type."""

    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get(self, request: Request) -> Response:
        is_read_param = request.query_params.get('is_read')
        is_read = None
        if is_read_param is not None:
            # Parsed manually rather than via serializers.BooleanField: a
            # missing query param must mean "no filter", not False — see
            # PROJECT_RULES.md's documented DRF BooleanField/query-param gotcha.
            if is_read_param.lower() not in ('true', 'false'):
                return Response(
                    {'detail': 'is_read must be true or false.', 'code': 'invalid_filter'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            is_read = is_read_param.lower() == 'true'

        notification_type = request.query_params.get('notification_type') or None

        queryset = list_notifications_for_user_filtered(
            request.user, is_read=is_read, notification_type=notification_type
        )

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = NotificationSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class NotificationUnreadCountView(APIView):
    """GET /api/v1/notifications/unread-count/ — backs the notification
    bell badge; polled via TanStack Query per ARCHITECTURE.md Section 6."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        return Response({'unread_count': get_unread_count_for_user(request.user)})


class NotificationMarkAllReadView(APIView):
    """POST /api/v1/notifications/mark-all-read/"""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        updated = mark_all_notifications_read(request.user)
        return Response({'updated': updated})


class NotificationDetailView(APIView):
    """
    GET    /api/v1/notifications/<id>/ — retrieve a notification.
    PATCH  /api/v1/notifications/<id>/ — update read state.
    DELETE /api/v1/notifications/<id>/ — soft-delete (dismiss).
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, notification_id) -> Response:
        try:
            notification = get_notification(request.user, notification_id)
        except NotificationNotFoundError as exc:
            return Response(
                {'detail': str(exc), 'code': 'notification_not_found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(NotificationSerializer(notification).data)

    def patch(self, request: Request, notification_id) -> Response:
        serializer = NotificationUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            notification = update_notification_read_state(
                request.user, notification_id, is_read=serializer.validated_data['is_read']
            )
        except NotificationNotFoundError as exc:
            return Response(
                {'detail': str(exc), 'code': 'notification_not_found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(NotificationSerializer(notification).data)

    def delete(self, request: Request, notification_id) -> Response:
        try:
            delete_notification_for_user(request.user, notification_id)
        except NotificationNotFoundError as exc:
            return Response(
                {'detail': str(exc), 'code': 'notification_not_found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class DeviceTokenListView(APIView):
    """POST /api/v1/notifications/devices/ — register a push device token
    for the current user."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        serializer = DeviceTokenWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        device = register_device_token_for_user(request.user, **serializer.validated_data)
        return Response(DeviceTokenSerializer(device).data, status=status.HTTP_201_CREATED)


class DeviceTokenDetailView(APIView):
    """DELETE /api/v1/notifications/devices/<id>/ — unregister a device
    token (e.g. on sign-out or push permission revocation)."""

    permission_classes = [IsAuthenticated]

    def delete(self, request: Request, device_id) -> Response:
        try:
            unregister_device_token_for_user(request.user, device_id)
        except DeviceTokenNotFoundError as exc:
            return Response(
                {'detail': str(exc), 'code': 'device_token_not_found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)
