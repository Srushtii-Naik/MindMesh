from django.db import connections
from django.db.utils import OperationalError
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    """
    Basic liveness health-check endpoint.

    Per ROADMAP.md Milestone 1 Deliverables: "Frontend and backend communicate
    over a basic health-check endpoint." Deliberately dependency-free — it
    only confirms the Django process itself is up and serving requests, so
    it can't report unhealthy due to a downstream outage it can't fix. See
    ReadinessView below for a check that also verifies the database and
    cache/broker are reachable, per Milestone 12's "Monitoring and logging
    in place" requirement.

    Explicitly public: the global DRF default became IsAuthenticated in
    Milestone 2.1, but a health check must be reachable without a session.
    """

    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        return Response({'status': 'ok'})


class ReadinessCheckView(APIView):
    """
    GET /api/v1/health/ready/

    Readiness probe for Milestone 12 ("Monitoring and logging in place with
    alerting for critical failures"): confirms the two services the backend
    cannot function without — PostgreSQL (system of record, ARCHITECTURE.md
    Section 4) and Redis (cache + Celery broker, ARCHITECTURE.md Section 8)
    — are actually reachable, not just that the Django process is running.

    Intended for platform-level health checks (Railway's healthcheck path,
    an uptime monitor, a load balancer) that should stop routing traffic to
    an instance that can't reach its dependencies, and alert on repeated
    failures. Returns 200 with a per-dependency breakdown when healthy, 503
    with the same breakdown when not — the body is useful for on-call
    triage either way.
    """

    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        checks = {'database': self._check_database(), 'cache': self._check_cache()}
        healthy = all(checks.values())
        return Response(
            {'status': 'ready' if healthy else 'unavailable', 'checks': checks},
            status=200 if healthy else 503,
        )

    @staticmethod
    def _check_database() -> bool:
        try:
            with connections['default'].cursor() as cursor:
                cursor.execute('SELECT 1')
            return True
        except OperationalError:
            return False

    @staticmethod
    def _check_cache() -> bool:
        from django.core.cache import cache

        try:
            cache.set('readiness-probe', '1', timeout=5)
            return cache.get('readiness-probe') == '1'
        except Exception:  # noqa: BLE001 — any cache backend failure means "not ready"
            return False
