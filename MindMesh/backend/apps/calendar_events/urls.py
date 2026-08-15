"""
URL routes — Calendar & Scheduling.

Mounted at /api/v1/calendar/ from config/urls.py, per ARCHITECTURE.md
Section 6 API versioning convention.
"""

from django.urls import path

from apps.calendar_events.views import (
    CalendarViewView,
    DailyPlannerView,
    EventDetailView,
    EventListCreateView,
    WeeklyPlannerView,
)

urlpatterns = [
    # Combined calendar view & planners
    path('view/', CalendarViewView.as_view(), name='calendar-view'),
    path('planner/daily/', DailyPlannerView.as_view(), name='calendar-planner-daily'),
    path('planner/weekly/', WeeklyPlannerView.as_view(), name='calendar-planner-weekly'),

    # Events
    path('events/', EventListCreateView.as_view(), name='calendar-event-list'),
    path('events/<uuid:event_id>/', EventDetailView.as_view(), name='calendar-event-detail'),
]
