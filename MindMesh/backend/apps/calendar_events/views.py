"""
DRF views — Calendar & Scheduling.

Handles HTTP concerns only (request parsing, status codes, response
shaping, pagination). Business logic is delegated to
apps.calendar_events.services, per ARCHITECTURE.md Section 3.
"""

from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.calendar_events.serializers import (
    CalendarRangeSerializer,
    CalendarViewSerializer,
    DailyPlannerQuerySerializer,
    DailyPlannerSerializer,
    EventFilterSerializer,
    EventSerializer,
    EventWriteSerializer,
    WeeklyPlannerQuerySerializer,
    WeeklyPlannerSerializer,
)
from apps.calendar_events.services import (
    EventNotFoundError,
    InvalidEventRangeError,
    LinkedTaskNotFoundError,
    create_event_for_user,
    delete_event_for_user,
    get_calendar_view,
    get_daily_planner,
    get_event,
    get_weekly_planner,
    list_events_for_user_filtered,
    update_event_for_user,
)


# --------------------------------------------------------------------------
# Events
# --------------------------------------------------------------------------


class EventListCreateView(APIView):
    """
    GET  /api/v1/calendar/events/ — list the user's events, filterable by
         start/end/task_id/search (ROADMAP.md Milestone 5: "Event CRUD
         implemented and validated").
    POST /api/v1/calendar/events/ — create an event.
    """

    permission_classes = [IsAuthenticated]

    pagination_class = PageNumberPagination

    def get(self, request: Request) -> Response:
        filters = EventFilterSerializer(data=request.query_params)
        filters.is_valid(raise_exception=True)

        queryset = list_events_for_user_filtered(request.user, **filters.validated_data)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = EventSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request: Request) -> Response:
        serializer = EventWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            event = create_event_for_user(request.user, **serializer.validated_data)
        except InvalidEventRangeError as exc:
            return Response(
                {'detail': str(exc), 'code': 'invalid_event_range'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except LinkedTaskNotFoundError as exc:
            return Response(
                {'detail': str(exc), 'code': 'task_not_found'},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(EventSerializer(event).data, status=status.HTTP_201_CREATED)


class EventDetailView(APIView):
    """
    GET    /api/v1/calendar/events/<id>/ — retrieve an event.
    PATCH  /api/v1/calendar/events/<id>/ — update an event's editable fields.
    DELETE /api/v1/calendar/events/<id>/ — soft-delete an event.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, event_id) -> Response:
        try:
            event = get_event(request.user, event_id)
        except EventNotFoundError as exc:
            return Response(
                {'detail': str(exc), 'code': 'event_not_found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(EventSerializer(event).data)

    def patch(self, request: Request, event_id) -> Response:
        serializer = EventWriteSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            event = update_event_for_user(request.user, event_id, **serializer.validated_data)
        except EventNotFoundError as exc:
            return Response(
                {'detail': str(exc), 'code': 'event_not_found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        except InvalidEventRangeError as exc:
            return Response(
                {'detail': str(exc), 'code': 'invalid_event_range'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except LinkedTaskNotFoundError as exc:
            return Response(
                {'detail': str(exc), 'code': 'task_not_found'},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(EventSerializer(event).data)

    def delete(self, request: Request, event_id) -> Response:
        try:
            delete_event_for_user(request.user, event_id)
        except EventNotFoundError as exc:
            return Response(
                {'detail': str(exc), 'code': 'event_not_found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


# --------------------------------------------------------------------------
# Combined calendar view & planners
# --------------------------------------------------------------------------


class CalendarViewView(APIView):
    """GET /api/v1/calendar/view/?start=YYYY-MM-DD&end=YYYY-MM-DD — events and
    task due dates for a date range, powering month/week grid rendering
    (ROADMAP.md Milestone 5: "Calendar views render correctly with real
    event/task data")."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        query = CalendarRangeSerializer(data=request.query_params)
        query.is_valid(raise_exception=True)

        view = get_calendar_view(
            request.user, query.validated_data['start'], query.validated_data['end']
        )
        return Response(CalendarViewSerializer(view).data)


class DailyPlannerView(APIView):
    """GET /api/v1/calendar/planner/daily/?date=YYYY-MM-DD — a single day's
    events and due tasks (ROADMAP.md Milestone 5: "Daily and weekly planners
    functional")."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        query = DailyPlannerQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)

        planner = get_daily_planner(request.user, query.validated_data['date'])
        return Response(DailyPlannerSerializer(planner).data)


class WeeklyPlannerView(APIView):
    """GET /api/v1/calendar/planner/weekly/?start=YYYY-MM-DD — a 7-day
    breakdown of events and due tasks starting from `start` (ROADMAP.md
    Milestone 5: "Daily and weekly planners functional")."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        query = WeeklyPlannerQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)

        planner = get_weekly_planner(request.user, query.validated_data['start'])
        return Response(WeeklyPlannerSerializer(planner).data)
