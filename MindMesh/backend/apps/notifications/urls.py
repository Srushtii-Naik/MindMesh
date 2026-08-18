"""URL routing — Notifications. Namespaced under /api/v1/notifications/ by
the project root config/urls.py."""

from django.urls import path

from apps.notifications.views import (
    DeviceTokenDetailView,
    DeviceTokenListView,
    NotificationDetailView,
    NotificationListView,
    NotificationMarkAllReadView,
    NotificationUnreadCountView,
)

urlpatterns = [
    # Static-segment routes registered before the <uuid:...> capture so
    # they can never be shadowed by it.
    path('unread-count/', NotificationUnreadCountView.as_view(), name='notification-unread-count'),
    path('mark-all-read/', NotificationMarkAllReadView.as_view(), name='notification-mark-all-read'),
    path('devices/', DeviceTokenListView.as_view(), name='device-token-list'),
    path('devices/<uuid:device_id>/', DeviceTokenDetailView.as_view(), name='device-token-detail'),
    path('', NotificationListView.as_view(), name='notification-list'),
    path('<uuid:notification_id>/', NotificationDetailView.as_view(), name='notification-detail'),
]
