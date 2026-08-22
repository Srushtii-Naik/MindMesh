"""
URL routes — Analytics & Insights.

Mounted at /api/v1/analytics/ from config/urls.py, per ARCHITECTURE.md
Section 6 API versioning convention.
"""

from django.urls import path

from apps.analytics.views import (
    HabitTrackingView,
    ProductivityAnalyticsView,
    ProgressReportDetailView,
    ProgressReportListView,
    RecommendationsView,
)

urlpatterns = [
    path('productivity/', ProductivityAnalyticsView.as_view(), name='analytics-productivity'),
    path('habits/', HabitTrackingView.as_view(), name='analytics-habits'),
    path(
        'recommendations/', RecommendationsView.as_view(), name='analytics-recommendations'
    ),
    path('reports/', ProgressReportListView.as_view(), name='analytics-report-list'),
    path(
        'reports/<uuid:report_id>/',
        ProgressReportDetailView.as_view(),
        name='analytics-report-detail',
    ),
]
