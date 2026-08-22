from django.urls import path

from common.views import HealthCheckView, ReadinessCheckView

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('health/ready/', ReadinessCheckView.as_view(), name='readiness-check'),
]
