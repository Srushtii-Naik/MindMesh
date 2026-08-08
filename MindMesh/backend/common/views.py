from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    """
    Basic health-check endpoint.

    Per ROADMAP.md Milestone 1 Deliverables: "Frontend and backend communicate
    over a basic health-check endpoint." This is the only functional endpoint
    expected to exist at the Project Foundation stage.

    Explicitly public: the global DRF default became IsAuthenticated in
    Milestone 2.1, but a health check must be reachable without a session.
    """

    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        return Response({'status': 'ok'})
