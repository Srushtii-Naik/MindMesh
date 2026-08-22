"""
DRF views — Analytics & Insights.

Handles HTTP concerns only (request parsing, status codes, response
shaping). Business logic is delegated to apps.analytics.services, per
ARCHITECTURE.md Section 3.
"""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.analytics.serializers import (
    HabitTrackingSerializer,
    ProductivityAnalyticsSerializer,
    ProgressReportSerializer,
    WindowQuerySerializer,
)
from apps.analytics.services import (
    DEFAULT_HABIT_WINDOW_DAYS,
    DEFAULT_PRODUCTIVITY_WINDOW_DAYS,
    ReportNotFoundError,
    get_ai_recommendations,
    get_habit_tracking,
    get_productivity_analytics,
    get_progress_report,
    list_progress_reports,
)


class ProductivityAnalyticsView(APIView):
    """GET /api/v1/analytics/productivity/?days=30 — task completion rate,
    totals, and a daily series, plus notes/events counts for the same
    window (ROADMAP.md Milestone 11)."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        query = WindowQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        days = query.validated_data.get('days', DEFAULT_PRODUCTIVITY_WINDOW_DAYS)

        analytics = get_productivity_analytics(request.user, days=days)
        return Response(ProductivityAnalyticsSerializer(analytics).data)


class HabitTrackingView(APIView):
    """GET /api/v1/analytics/habits/?days=90 — daily task-completion streak
    and a heatmap-ready activity series (ROADMAP.md Milestone 11)."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        query = WindowQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        days = query.validated_data.get('days', DEFAULT_HABIT_WINDOW_DAYS)

        habits = get_habit_tracking(request.user, days=days)
        return Response(HabitTrackingSerializer(habits).data)


class RecommendationsView(APIView):
    """GET /api/v1/analytics/recommendations/ — AI-generated recommendations
    surfaced through the AI abstraction layer (ROADMAP.md Milestone 11).
    Returns an empty list (never an error) if the provider is unavailable —
    recommendations are advisory, not load-bearing."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        recommendations = get_ai_recommendations(request.user)
        return Response({'recommendations': recommendations})


class ProgressReportListView(APIView):
    """GET /api/v1/analytics/reports/ — the user's generated progress
    reports, most recent first (ROADMAP.md Milestone 11). Reports are
    produced by the weekly Celery Beat task
    (apps.analytics.tasks.generate_weekly_reports_task), not created here."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        reports = list_progress_reports(request.user)
        return Response(ProgressReportSerializer(reports, many=True).data)


class ProgressReportDetailView(APIView):
    """GET /api/v1/analytics/reports/<id>/ — a single progress report."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, report_id) -> Response:
        try:
            report = get_progress_report(request.user, report_id)
        except ReportNotFoundError as exc:
            return Response(
                {'detail': str(exc), 'code': 'progress_report_not_found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(ProgressReportSerializer(report).data)
