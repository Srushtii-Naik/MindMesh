"""
DRF views — Family & Shared Workspace.

Handles HTTP concerns only (request parsing, status codes, response
shaping). Business logic is delegated to apps.family.services, per
ARCHITECTURE.md Section 3.
"""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.family import services
from apps.family.serializers import (
    EmergencyContactSerializer,
    EmergencyContactWriteSerializer,
    FamilyInvitationSerializer,
    FamilyMembershipSerializer,
    FamilySerializer,
    FamilyWriteSerializer,
    InviteMemberWriteSerializer,
    MemberRoleWriteSerializer,
    ShareResourceWriteSerializer,
    SharedEventSerializer,
    SharedNoteSerializer,
    SharedTaskSerializer,
    SharePermissionWriteSerializer,
)
from apps.tasks.serializers import TaskWriteSerializer

# --------------------------------------------------------------------------
# Uniform error mapping
# --------------------------------------------------------------------------
# Every apps.family.services error maps to an HTTP status + machine-readable
# code, mirroring the per-exception Response pattern used across
# apps.tasks/apps.notifications, but centralized here since this module has
# a wider exception surface (invitations, membership, and three flavors of
# shared-resource errors) than any single existing view module.

_ERROR_MAP = {
    services.FamilyNotFoundError: (status.HTTP_404_NOT_FOUND, 'family_not_found'),
    services.NotFamilyMemberError: (status.HTTP_403_FORBIDDEN, 'not_family_member'),
    services.InsufficientFamilyPermissionError: (
        status.HTTP_403_FORBIDDEN, 'insufficient_family_permission',
    ),
    services.AlreadyInFamilyError: (status.HTTP_409_CONFLICT, 'already_in_family'),
    services.MembershipNotFoundError: (status.HTTP_404_NOT_FOUND, 'membership_not_found'),
    services.CannotRemoveLastOwnerError: (status.HTTP_409_CONFLICT, 'cannot_remove_last_owner'),
    services.InvitationNotFoundError: (status.HTTP_404_NOT_FOUND, 'invitation_not_found'),
    services.InvitationNotPendingError: (status.HTTP_409_CONFLICT, 'invitation_not_pending'),
    services.InvitationExpiredError: (status.HTTP_410_GONE, 'invitation_expired'),
    services.InvitationEmailMismatchError: (status.HTTP_403_FORBIDDEN, 'invitation_email_mismatch'),
    services.AlreadyFamilyMemberError: (status.HTTP_409_CONFLICT, 'already_family_member'),
    services.EmergencyContactNotFoundError: (
        status.HTTP_404_NOT_FOUND, 'emergency_contact_not_found',
    ),
    services.SharedResourceNotFoundError: (status.HTTP_404_NOT_FOUND, 'shared_resource_not_found'),
    services.ResourceNotFoundError: (status.HTTP_404_NOT_FOUND, 'resource_not_found'),
    services.ResourceAlreadySharedError: (status.HTTP_409_CONFLICT, 'resource_already_shared'),
    services.SharePermissionDeniedError: (status.HTTP_403_FORBIDDEN, 'share_permission_denied'),
}

_FAMILY_SERVICE_ERRORS = tuple(_ERROR_MAP.keys())


def _error_response(exc: Exception) -> Response:
    http_status, code = _ERROR_MAP[type(exc)]
    return Response({'detail': str(exc), 'code': code}, status=http_status)


# --------------------------------------------------------------------------
# Family
# --------------------------------------------------------------------------


class MyFamilyView(APIView):
    """
    GET  /api/v1/family/me/ — the current user's family (404 if none).
    POST /api/v1/family/    — create a new family (the requester becomes owner).
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        family = services.get_family_for_user(request.user)
        if family is None:
            return Response(
                {'detail': 'You do not belong to a family yet.', 'code': 'family_not_found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(FamilySerializer(family).data)

    def post(self, request: Request) -> Response:
        serializer = FamilyWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            family = services.create_family_for_user(request.user, **serializer.validated_data)
        except _FAMILY_SERVICE_ERRORS as exc:
            return _error_response(exc)

        return Response(FamilySerializer(family).data, status=status.HTTP_201_CREATED)


class FamilyDetailView(APIView):
    """PATCH /api/v1/family/<family_id>/ — rename the family (owner/adult only)."""

    permission_classes = [IsAuthenticated]

    def patch(self, request: Request, family_id) -> Response:
        serializer = FamilyWriteSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            family = services.update_family_for_user(
                request.user, family_id, **serializer.validated_data
            )
        except _FAMILY_SERVICE_ERRORS as exc:
            return _error_response(exc)

        return Response(FamilySerializer(family).data)


class FamilyLeaveView(APIView):
    """POST /api/v1/family/<family_id>/leave/ — the requester leaves the family."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request, family_id) -> Response:
        try:
            services.leave_family(request.user, family_id)
        except _FAMILY_SERVICE_ERRORS as exc:
            return _error_response(exc)
        return Response(status=status.HTTP_204_NO_CONTENT)


# --------------------------------------------------------------------------
# Members
# --------------------------------------------------------------------------


class FamilyMemberListView(APIView):
    """GET /api/v1/family/<family_id>/members/ — list active members."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, family_id) -> Response:
        try:
            members = services.list_members(request.user, family_id)
        except _FAMILY_SERVICE_ERRORS as exc:
            return _error_response(exc)
        return Response(FamilyMembershipSerializer(members, many=True).data)


class FamilyMemberDetailView(APIView):
    """
    PATCH  /api/v1/family/<family_id>/members/<membership_id>/ — change role (owner only).
    DELETE /api/v1/family/<family_id>/members/<membership_id>/ — remove member (owner only).
    """

    permission_classes = [IsAuthenticated]

    def patch(self, request: Request, family_id, membership_id) -> Response:
        serializer = MemberRoleWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            membership = services.update_member_role(
                request.user, family_id, membership_id, **serializer.validated_data
            )
        except _FAMILY_SERVICE_ERRORS as exc:
            return _error_response(exc)

        return Response(FamilyMembershipSerializer(membership).data)

    def delete(self, request: Request, family_id, membership_id) -> Response:
        try:
            services.remove_member(request.user, family_id, membership_id)
        except _FAMILY_SERVICE_ERRORS as exc:
            return _error_response(exc)
        return Response(status=status.HTTP_204_NO_CONTENT)


# --------------------------------------------------------------------------
# Invitations
# --------------------------------------------------------------------------


class FamilyInvitationListCreateView(APIView):
    """
    GET  /api/v1/family/<family_id>/invitations/ — list invitations sent by this family
         (owner/adult only).
    POST /api/v1/family/<family_id>/invitations/ — invite a member (owner/adult only).
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, family_id) -> Response:
        try:
            invitations = services.list_invitations_for_family_id(request.user, family_id)
        except _FAMILY_SERVICE_ERRORS as exc:
            return _error_response(exc)
        return Response(FamilyInvitationSerializer(invitations, many=True).data)

    def post(self, request: Request, family_id) -> Response:
        serializer = InviteMemberWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            invitation = services.invite_member(
                request.user, family_id, **serializer.validated_data
            )
        except _FAMILY_SERVICE_ERRORS as exc:
            return _error_response(exc)

        return Response(FamilyInvitationSerializer(invitation).data, status=status.HTTP_201_CREATED)


class FamilyInvitationCancelView(APIView):
    """DELETE /api/v1/family/<family_id>/invitations/<invitation_id>/ — cancel a pending invite."""

    permission_classes = [IsAuthenticated]

    def delete(self, request: Request, family_id, invitation_id) -> Response:
        try:
            services.cancel_invitation(request.user, family_id, invitation_id)
        except _FAMILY_SERVICE_ERRORS as exc:
            return _error_response(exc)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MyInvitationListView(APIView):
    """GET /api/v1/family/invitations/ — pending invitations addressed to the current user."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        invitations = services.list_invitations_for_user(request.user)
        return Response(FamilyInvitationSerializer(invitations, many=True).data)


class InvitationAcceptView(APIView):
    """POST /api/v1/family/invitations/<token>/accept/"""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request, token) -> Response:
        try:
            services.accept_invitation(request.user, token)
            family = services.get_family_for_user(request.user)
        except _FAMILY_SERVICE_ERRORS as exc:
            return _error_response(exc)
        return Response(FamilySerializer(family).data, status=status.HTTP_200_OK)


class InvitationDeclineView(APIView):
    """POST /api/v1/family/invitations/<token>/decline/"""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request, token) -> Response:
        try:
            invitation = services.decline_invitation(request.user, token)
        except _FAMILY_SERVICE_ERRORS as exc:
            return _error_response(exc)
        return Response(FamilyInvitationSerializer(invitation).data)


# --------------------------------------------------------------------------
# Emergency contacts
# --------------------------------------------------------------------------


class EmergencyContactListCreateView(APIView):
    """
    GET  /api/v1/family/<family_id>/emergency-contacts/ — list (any active member).
    POST /api/v1/family/<family_id>/emergency-contacts/ — create (owner/adult only).
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, family_id) -> Response:
        try:
            contacts = services.list_emergency_contacts(request.user, family_id)
        except _FAMILY_SERVICE_ERRORS as exc:
            return _error_response(exc)
        return Response(EmergencyContactSerializer(contacts, many=True).data)

    def post(self, request: Request, family_id) -> Response:
        serializer = EmergencyContactWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            contact = services.create_emergency_contact_for_user(
                request.user, family_id, **serializer.validated_data
            )
        except _FAMILY_SERVICE_ERRORS as exc:
            return _error_response(exc)

        return Response(EmergencyContactSerializer(contact).data, status=status.HTTP_201_CREATED)


class EmergencyContactDetailView(APIView):
    """
    GET    /api/v1/family/<family_id>/emergency-contacts/<contact_id>/
    PATCH  /api/v1/family/<family_id>/emergency-contacts/<contact_id>/ — owner/adult only.
    DELETE /api/v1/family/<family_id>/emergency-contacts/<contact_id>/ — owner/adult only.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, family_id, contact_id) -> Response:
        try:
            contact = services.get_emergency_contact(request.user, family_id, contact_id)
        except _FAMILY_SERVICE_ERRORS as exc:
            return _error_response(exc)
        return Response(EmergencyContactSerializer(contact).data)

    def patch(self, request: Request, family_id, contact_id) -> Response:
        serializer = EmergencyContactWriteSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            contact = services.update_emergency_contact_for_user(
                request.user, family_id, contact_id, **serializer.validated_data
            )
        except _FAMILY_SERVICE_ERRORS as exc:
            return _error_response(exc)

        return Response(EmergencyContactSerializer(contact).data)

    def delete(self, request: Request, family_id, contact_id) -> Response:
        try:
            services.delete_emergency_contact_for_user(request.user, family_id, contact_id)
        except _FAMILY_SERVICE_ERRORS as exc:
            return _error_response(exc)
        return Response(status=status.HTTP_204_NO_CONTENT)


# --------------------------------------------------------------------------
# Shared resources
# --------------------------------------------------------------------------


class _BaseSharedResourceListCreateView(APIView):
    """Shared base for the three (task/event/note) shared-resource list+create
    views — see subclasses below for the resource_type each binds to."""

    permission_classes = [IsAuthenticated]
    resource_type: str = ''
    item_serializer_class = None
    list_fn = None

    def get(self, request: Request, family_id) -> Response:
        try:
            items = self.list_fn(request.user, family_id)
        except _FAMILY_SERVICE_ERRORS as exc:
            return _error_response(exc)
        return Response(self.item_serializer_class(items, many=True).data)

    def post(self, request: Request, family_id) -> Response:
        serializer = ShareResourceWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            shared = services.share_resource(
                request.user, family_id, resource_type=self.resource_type,
                **serializer.validated_data,
            )
        except _FAMILY_SERVICE_ERRORS as exc:
            return _error_response(exc)

        return Response(
            {
                'id': str(shared.id),
                'resource_type': shared.resource_type,
                'can_edit': shared.can_edit,
            },
            status=status.HTTP_201_CREATED,
        )


class _BaseSharedResourceDetailView(APIView):
    """Shared base for unsharing / updating permission on a single shared item."""

    permission_classes = [IsAuthenticated]
    resource_type: str = ''

    def patch(self, request: Request, family_id, shared_id) -> Response:
        serializer = SharePermissionWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            shared = services.update_share_permission(
                request.user, family_id, shared_id, self.resource_type,
                **serializer.validated_data,
            )
        except _FAMILY_SERVICE_ERRORS as exc:
            return _error_response(exc)

        return Response({'id': str(shared.id), 'can_edit': shared.can_edit})

    def delete(self, request: Request, family_id, shared_id) -> Response:
        try:
            services.unshare_resource(request.user, family_id, shared_id, self.resource_type)
        except _FAMILY_SERVICE_ERRORS as exc:
            return _error_response(exc)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SharedTaskListCreateView(_BaseSharedResourceListCreateView):
    """
    GET  /api/v1/family/<family_id>/shared-tasks/ — list tasks shared with the family.
    POST /api/v1/family/<family_id>/shared-tasks/ — share one of the requester's own tasks.
    """

    resource_type = 'task'
    item_serializer_class = SharedTaskSerializer
    list_fn = staticmethod(services.list_shared_tasks)


class SharedTaskDetailView(_BaseSharedResourceDetailView):
    """
    PATCH  /api/v1/family/<family_id>/shared-tasks/<shared_id>/ — update sharing permission.
    DELETE /api/v1/family/<family_id>/shared-tasks/<shared_id>/ — unshare.
    """

    resource_type = 'task'


class SharedTaskEditView(APIView):
    """PATCH /api/v1/family/<family_id>/shared-tasks/<shared_id>/task/ — edit the underlying
    task (owner, or any member if can_edit), per PRD.md Section 6.4's task-delegation story."""

    permission_classes = [IsAuthenticated]

    def patch(self, request: Request, family_id, shared_id) -> Response:
        serializer = TaskWriteSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            task = services.update_shared_task(
                request.user, family_id, shared_id, **serializer.validated_data
            )
        except _FAMILY_SERVICE_ERRORS as exc:
            return _error_response(exc)

        from apps.tasks.serializers import TaskSerializer

        return Response(TaskSerializer(task).data)


class SharedTaskCompleteView(APIView):
    """POST /api/v1/family/<family_id>/shared-tasks/<shared_id>/complete/"""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request, family_id, shared_id) -> Response:
        try:
            task = services.complete_shared_task(request.user, family_id, shared_id)
        except _FAMILY_SERVICE_ERRORS as exc:
            return _error_response(exc)

        from apps.tasks.serializers import TaskSerializer

        return Response(TaskSerializer(task).data)


class SharedEventListCreateView(_BaseSharedResourceListCreateView):
    """
    GET  /api/v1/family/<family_id>/shared-events/ — list events shared with the family.
    POST /api/v1/family/<family_id>/shared-events/ — share one of the requester's own events.
    """

    resource_type = 'event'
    item_serializer_class = SharedEventSerializer
    list_fn = staticmethod(services.list_shared_events)


class SharedEventDetailView(_BaseSharedResourceDetailView):
    """DELETE /api/v1/family/<family_id>/shared-events/<shared_id>/ — unshare.
    Events are view-only for non-owners this milestone (see ROADMAP.md
    Milestone 10 scope note in apps/family/services.py), so PATCH only
    updates the share permission flag, not the event itself."""

    resource_type = 'event'


class SharedNoteListCreateView(_BaseSharedResourceListCreateView):
    """
    GET  /api/v1/family/<family_id>/shared-notes/ — list notes shared with the family.
    POST /api/v1/family/<family_id>/shared-notes/ — share one of the requester's own notes.
    """

    resource_type = 'note'
    item_serializer_class = SharedNoteSerializer
    list_fn = staticmethod(services.list_shared_notes)


class SharedNoteDetailView(_BaseSharedResourceDetailView):
    """DELETE /api/v1/family/<family_id>/shared-notes/<shared_id>/ — unshare.
    Notes are view-only for non-owners this milestone (same rationale as events)."""

    resource_type = 'note'
