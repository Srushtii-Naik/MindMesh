"""
Tests for the liveness (/health/) and readiness (/health/ready/) endpoints.

Milestone 1 established the liveness check; Milestone 12 adds readiness
(ROADMAP.md — "Monitoring and logging in place with alerting for critical
failures").
"""

from unittest.mock import patch

import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_health_check_is_public_and_returns_ok(api_client):
    response = api_client.get(reverse('health-check'))

    assert response.status_code == 200
    assert response.data == {'status': 'ok'}


def test_readiness_check_is_public_and_healthy_by_default(api_client):
    response = api_client.get(reverse('readiness-check'))

    assert response.status_code == 200
    assert response.data['status'] == 'ready'
    assert response.data['checks'] == {'database': True, 'cache': True}


def test_readiness_check_returns_503_when_database_unreachable(api_client):
    from common.views import ReadinessCheckView

    with patch.object(ReadinessCheckView, '_check_database', return_value=False):
        response = api_client.get(reverse('readiness-check'))

    assert response.status_code == 503
    assert response.data['status'] == 'unavailable'
    assert response.data['checks']['database'] is False


def test_readiness_check_returns_503_when_cache_unreachable(api_client):
    from common.views import ReadinessCheckView

    with patch.object(ReadinessCheckView, '_check_cache', return_value=False):
        response = api_client.get(reverse('readiness-check'))

    assert response.status_code == 503
    assert response.data['checks']['cache'] is False
