"""
Service layer — Family & Shared Workspace.

Domain business logic for family creation/management, invitations,
emergency contacts, and cross-domain resource sharing. Per ARCHITECTURE.md
Section 3: views call services; services never import DRF.

Sharing resolves the underlying task/event/note through the owning domain's
own service interface (apps.tasks.services / apps.calendar_events.services /
apps.notes.services) rather than importing their models directly, per
ARCHITECTURE.md Section 3's cross-domain communication rule.
"""

from __future__ import annotations

from datetime import timedelta

from django.utils import timezone

from apps.accounts.models import User
from apps.family.models import (
    EmergencyContact,
    Family,
    FamilyInvitation,
    FamilyMembership,
    FamilyRole,
    InvitationStatus,
    SharedResource,
    SharedResourceType,
)
from apps.family.repositories import (
    count_active_members,
    count_active_owners,
    create_emergency_contact,
    create_family,
    create_invitation,
    create_membership,
    create_shared_resource,
    deactivate_membership,
    get_active_membership_for_user,
    get_active_share_for_resource,
    get_emergency_contact_for_family,
    get_family_by_id,
    get_invitation_by_token,
    get_invitation_for_family,
    get_membership_by_id,
    get_membership_for_user_family,
    get_shared_resource_for_family,
    has_pending_invitation,
    list_active_memberships_for_family,
    list_emergency_contacts_for_family,
    list_invitations_for_family,
    list_pending_invitations_for_email,
    list_shared_resources_for_family,
    soft_delete_emergency_contact,
    soft_delete_family,
    soft_delete_shared_resource,
    update_emergency_contact,
    update_family,
    update_invitation,
    update_membership,
    update_shared_resource,
)

INVITATION_VALIDITY = timedelta(days=7)

# Roles permitted to manage membership, invitations, and emergency contacts
# (PRD.md Section 6.4/6.1: parent/adult oversight, restricted child surface).
_MANAGING_ROLES = (FamilyRole.OWNER, FamilyRole.ADULT)


# --------------------------------------------------------------------------
# Exceptions
# --------------------------------------------------------------------------


class FamilyNotFoundError(Exception):
    """Raised when a family cannot be found."""


class NotFamilyMemberError(Exception):
    """Raised when the requesting user is not an active member of the family."""


class InsufficientFamilyPermissionError(Exception):
    """Raised when a CHILD-role member attempts a management action."""


class AlreadyInFamilyError(Exception):
    """Raised when a user who already belongs to a family tries to join/create another."""


class MembershipNotFoundError(Exception):
    """Raised when a membership cannot be found within the given family."""


class CannotRemoveLastOwnerError(Exception):
    """Raised when removing/demoting a member would leave the family without an owner."""


class InvitationNotFoundError(Exception):
    """Raised when an invitation cannot be found."""


class InvitationNotPendingError(Exception):
    """Raised when responding to (or canceling) an invitation that isn't pending."""


class InvitationExpiredError(Exception):
    """Raised when accepting/declining an invitation past its expiry."""


class InvitationEmailMismatchError(Exception):
    """Raised when the responding user's email doesn't match the invited email."""


class AlreadyFamilyMemberError(Exception):
    """Raised when inviting someone who is already an active member."""


class EmergencyContactNotFoundError(Exception):
    """Raised when an emergency contact cannot be found within the given family."""


class SharedResourceNotFoundError(Exception):
    """Raised when a shared-resource record cannot be found within the given family."""


class ResourceNotFoundError(Exception):
    """Raised when the underlying task/event/note being shared doesn't exist for its owner."""


class ResourceAlreadySharedError(Exception):
    """Raised when a resource is already actively shared with the family."""


class SharePermissionDeniedError(Exception):
    """Raised when acting on a shared resource without the required permission."""


# --------------------------------------------------------------------------
# Internal helpers
# --------------------------------------------------------------------------


def _get_membership_or_raise(user: User, family_id) -> FamilyMembership:
    membership = get_membership_for_user_family(user, family_id)
    if membership is None:
        raise NotFamilyMemberError('You are not a member of this family.')
    return membership


def _require_managing_role(membership: FamilyMembership) -> None:
    if membership.role not in _MANAGING_ROLES:
        raise InsufficientFamilyPermissionError(
            'Only family owners and adults can perform this action.'
        )


def get_family(family_id) -> Family:
    family = get_family_by_id(family_id)
    if family is None:
        raise FamilyNotFoundError('Family not found.')
    return family


# --------------------------------------------------------------------------
# Family creation & membership
# --------------------------------------------------------------------------


def get_family_for_user(user: User) -> Family | None:
    """Returns the user's current family, or None if they don't belong to one."""
    membership = get_active_membership_for_user(user)
    return membership.family if membership else None


def create_family_for_user(user: User, *, name: str) -> Family:
    if get_active_membership_for_user(user) is not None:
        raise AlreadyInFamilyError(
            'You already belong to a family. Leave it before creating a new one.'
        )

    family = create_family(name=name.strip(), created_by=user)
    create_membership(family=family, user=user, role=FamilyRole.OWNER)
    return family


def update_family_for_user(user: User, family_id, **fields) -> Family:
    family = get_family(family_id)
    membership = _get_membership_or_raise(user, family_id)
    _require_managing_role(membership)

    if 'name' in fields:
        fields['name'] = fields['name'].strip()

    return update_family(family, **fields)


def list_members(user: User, family_id):
    get_family(family_id)
    _get_membership_or_raise(user, family_id)
    return list_active_memberships_for_family(get_family(family_id))


def update_member_role(user: User, family_id, membership_id, *, role: str) -> FamilyMembership:
    family = get_family(family_id)
    requester_membership = _get_membership_or_raise(user, family_id)
    if requester_membership.role != FamilyRole.OWNER:
        raise InsufficientFamilyPermissionError('Only a family owner can change member roles.')

    target = get_membership_by_id(family_id, membership_id)
    if target is None:
        raise MembershipNotFoundError('Membership not found.')

    if target.role == FamilyRole.OWNER and role != FamilyRole.OWNER:
        if count_active_owners(family) <= 1:
            raise CannotRemoveLastOwnerError(
                'Promote another member to owner before demoting the last owner.'
            )

    return update_membership(target, role=role)


def remove_member(user: User, family_id, membership_id) -> None:
    family = get_family(family_id)
    requester_membership = _get_membership_or_raise(user, family_id)
    if requester_membership.role != FamilyRole.OWNER:
        raise InsufficientFamilyPermissionError('Only a family owner can remove members.')

    target = get_membership_by_id(family_id, membership_id)
    if target is None:
        raise MembershipNotFoundError('Membership not found.')

    if target.role == FamilyRole.OWNER and count_active_owners(family) <= 1:
        raise CannotRemoveLastOwnerError(
            'Promote another member to owner before removing the last owner.'
        )

    deactivate_membership(target)


def leave_family(user: User, family_id) -> None:
    """A member removes themself. A sole owner with other members still
    present must promote someone else first (update_member_role) — leaving
    outright would strand the family without an owner. A sole owner who is
    also the sole member may leave freely; the family is soft-deleted along
    with them, since nothing remains to coordinate."""
    family = get_family(family_id)
    membership = _get_membership_or_raise(user, family_id)

    if membership.role == FamilyRole.OWNER and count_active_owners(family) <= 1:
        if count_active_members(family) > 1:
            raise CannotRemoveLastOwnerError(
                'Promote another member to owner before leaving the family.'
            )
        deactivate_membership(membership)
        soft_delete_family(family)
        return

    deactivate_membership(membership)


# --------------------------------------------------------------------------
# Invitations
# --------------------------------------------------------------------------


def invite_member(user: User, family_id, *, email: str, role: str) -> FamilyInvitation:
    family = get_family(family_id)
    membership = _get_membership_or_raise(user, family_id)
    _require_managing_role(membership)

    email = email.strip().lower()
    if role == FamilyRole.OWNER:
        role = FamilyRole.ADULT  # Ownership is granted via update_member_role, not invitation.

    active_members = list_active_memberships_for_family(family)
    if any(m.user.email.lower() == email for m in active_members):
        raise AlreadyFamilyMemberError('This person is already a member of the family.')

    if has_pending_invitation(family, email):
        raise AlreadyFamilyMemberError('An invitation is already pending for this email.')

    invitation = create_invitation(
        family=family,
        invited_email=email,
        role=role,
        invited_by=user,
        expires_at=timezone.now() + INVITATION_VALIDITY,
    )

    _notify_invited_user_if_registered(invitation)
    return invitation


def _notify_invited_user_if_registered(invitation: FamilyInvitation) -> None:
    """If the invited email already belongs to a MindMesh account, surface an
    in-app notification through the existing Notifications module
    (ARCHITECTURE.md Section 4/ROADMAP.md Milestone 9's cross-module
    notification center) rather than inventing a parallel channel here."""
    from apps.accounts.repositories import get_user_by_email
    from apps.notifications.models import NotificationType
    from apps.notifications.services import create_notification_for_user

    invited_user = get_user_by_email(invitation.invited_email)
    if invited_user is None:
        return

    create_notification_for_user(
        invited_user,
        notification_type=NotificationType.SYSTEM,
        title=f'{invitation.invited_by.full_name} invited you to join "{invitation.family.name}"',
        message='Open Family to accept or decline this invitation.',
    )


def list_invitations_for_family_id(user: User, family_id):
    get_family(family_id)
    membership = _get_membership_or_raise(user, family_id)
    _require_managing_role(membership)
    return list_invitations_for_family(get_family(family_id))


def list_invitations_for_user(user: User):
    return list_pending_invitations_for_email(user.email)


def cancel_invitation(user: User, family_id, invitation_id) -> None:
    get_family(family_id)
    membership = _get_membership_or_raise(user, family_id)
    _require_managing_role(membership)

    invitation = get_invitation_for_family(family_id, invitation_id)
    if invitation is None:
        raise InvitationNotFoundError('Invitation not found.')
    if invitation.status != InvitationStatus.PENDING:
        raise InvitationNotPendingError('Only a pending invitation can be canceled.')

    update_invitation(invitation, status=InvitationStatus.CANCELED, responded_at=timezone.now())


def _get_valid_pending_invitation(token) -> FamilyInvitation:
    invitation = get_invitation_by_token(token)
    if invitation is None:
        raise InvitationNotFoundError('Invitation not found.')
    if invitation.status != InvitationStatus.PENDING:
        raise InvitationNotPendingError('This invitation has already been responded to.')
    if invitation.expires_at < timezone.now():
        update_invitation(invitation, status=InvitationStatus.EXPIRED)
        raise InvitationExpiredError('This invitation has expired.')
    return invitation


def accept_invitation(user: User, token) -> FamilyMembership:
    invitation = _get_valid_pending_invitation(token)
    if invitation.invited_email.lower() != user.email.lower():
        raise InvitationEmailMismatchError('This invitation was sent to a different email address.')
    if get_active_membership_for_user(user) is not None:
        raise AlreadyInFamilyError('You already belong to a family. Leave it before accepting.')

    update_invitation(invitation, status=InvitationStatus.ACCEPTED, responded_at=timezone.now())
    return create_membership(family=invitation.family, user=user, role=invitation.role)


def decline_invitation(user: User, token) -> FamilyInvitation:
    invitation = _get_valid_pending_invitation(token)
    if invitation.invited_email.lower() != user.email.lower():
        raise InvitationEmailMismatchError('This invitation was sent to a different email address.')

    return update_invitation(
        invitation, status=InvitationStatus.DECLINED, responded_at=timezone.now()
    )


# --------------------------------------------------------------------------
# Emergency contacts
# --------------------------------------------------------------------------


def list_emergency_contacts(user: User, family_id):
    get_family(family_id)
    _get_membership_or_raise(user, family_id)  # any active member may view
    return list_emergency_contacts_for_family(get_family(family_id))


def get_emergency_contact(user: User, family_id, contact_id) -> EmergencyContact:
    get_family(family_id)
    _get_membership_or_raise(user, family_id)
    contact = get_emergency_contact_for_family(family_id, contact_id)
    if contact is None:
        raise EmergencyContactNotFoundError('Emergency contact not found.')
    return contact


def create_emergency_contact_for_user(user: User, family_id, **fields) -> EmergencyContact:
    family = get_family(family_id)
    membership = _get_membership_or_raise(user, family_id)
    _require_managing_role(membership)

    if 'name' in fields:
        fields['name'] = fields['name'].strip()
    return create_emergency_contact(family=family, added_by=user, **fields)


def update_emergency_contact_for_user(
    user: User, family_id, contact_id, **fields
) -> EmergencyContact:
    get_family(family_id)
    membership = _get_membership_or_raise(user, family_id)
    _require_managing_role(membership)

    contact = get_emergency_contact_for_family(family_id, contact_id)
    if contact is None:
        raise EmergencyContactNotFoundError('Emergency contact not found.')

    if 'name' in fields:
        fields['name'] = fields['name'].strip()
    return update_emergency_contact(contact, **fields)


def delete_emergency_contact_for_user(user: User, family_id, contact_id) -> None:
    get_family(family_id)
    membership = _get_membership_or_raise(user, family_id)
    _require_managing_role(membership)

    contact = get_emergency_contact_for_family(family_id, contact_id)
    if contact is None:
        raise EmergencyContactNotFoundError('Emergency contact not found.')
    soft_delete_emergency_contact(contact)


# --------------------------------------------------------------------------
# Shared resources — cross-domain resolution
# --------------------------------------------------------------------------


def _resolve_owned_resource(owner: User, resource_type: str, resource_id):
    """Fetches the underlying task/event/note through its own domain's
    service interface, confirming `owner` actually owns it. Raises
    ResourceNotFoundError uniformly regardless of domain."""
    if resource_type == SharedResourceType.TASK:
        from apps.tasks.services import TaskNotFoundError, get_task

        try:
            return get_task(owner, resource_id)
        except TaskNotFoundError as exc:
            raise ResourceNotFoundError(str(exc)) from exc

    if resource_type == SharedResourceType.EVENT:
        from apps.calendar_events.services import EventNotFoundError, get_event

        try:
            return get_event(owner, resource_id)
        except EventNotFoundError as exc:
            raise ResourceNotFoundError(str(exc)) from exc

    if resource_type == SharedResourceType.NOTE:
        from apps.notes.services import NoteNotFoundError, get_note

        try:
            return get_note(owner, resource_id)
        except NoteNotFoundError as exc:
            raise ResourceNotFoundError(str(exc)) from exc

    raise ValueError(f'Unsupported resource_type: {resource_type}')


def share_resource(
    user: User, family_id, *, resource_type: str, resource_id, can_edit: bool = False
) -> SharedResource:
    """Shares one of the requesting user's own tasks/events/notes with their
    family. Only the resource's owner may share it."""
    family = get_family(family_id)
    _get_membership_or_raise(user, family_id)

    _resolve_owned_resource(user, resource_type, resource_id)  # raises if not owned/found

    if get_active_share_for_resource(family, resource_type, resource_id) is not None:
        raise ResourceAlreadySharedError('This item is already shared with your family.')

    return create_shared_resource(
        family=family,
        resource_type=resource_type,
        resource_id=resource_id,
        owner=user,
        shared_by=user,
        can_edit=can_edit,
    )


def _get_shared_resource_or_raise(family_id, shared_id, resource_type: str) -> SharedResource:
    shared = get_shared_resource_for_family(family_id, shared_id)
    if shared is None or shared.resource_type != resource_type:
        raise SharedResourceNotFoundError('Shared item not found.')
    return shared


def unshare_resource(user: User, family_id, shared_id, resource_type: str) -> None:
    get_family(family_id)
    membership = _get_membership_or_raise(user, family_id)
    shared = _get_shared_resource_or_raise(family_id, shared_id, resource_type)

    if shared.owner_id != user.id and membership.role != FamilyRole.OWNER:
        raise SharePermissionDeniedError(
            'Only the item\'s owner or a family owner can unshare it.'
        )

    soft_delete_shared_resource(shared)


def update_share_permission(
    user: User, family_id, shared_id, resource_type: str, *, can_edit: bool
) -> SharedResource:
    get_family(family_id)
    _get_membership_or_raise(user, family_id)
    shared = _get_shared_resource_or_raise(family_id, shared_id, resource_type)

    if shared.owner_id != user.id:
        raise SharePermissionDeniedError("Only the item's owner can change its sharing permission.")

    return update_shared_resource(shared, can_edit=can_edit)


def _list_shared(user: User, family_id, resource_type: str) -> list[dict]:
    """Lists every active share of `resource_type` in the family, resolving
    each to its underlying resource. A share whose resource has since been
    deleted at the source is skipped (and its stale share record cleaned
    up) rather than surfaced as a broken entry."""
    family = get_family(family_id)
    _get_membership_or_raise(user, family_id)

    results = []
    for shared in list_shared_resources_for_family(family, resource_type):
        try:
            resource = _resolve_owned_resource(shared.owner, resource_type, shared.resource_id)
        except ResourceNotFoundError:
            soft_delete_shared_resource(shared)
            continue
        results.append({'share': shared, 'resource': resource})
    return results


def list_shared_tasks(user: User, family_id) -> list[dict]:
    return _list_shared(user, family_id, SharedResourceType.TASK)


def list_shared_events(user: User, family_id) -> list[dict]:
    return _list_shared(user, family_id, SharedResourceType.EVENT)


def list_shared_notes(user: User, family_id) -> list[dict]:
    return _list_shared(user, family_id, SharedResourceType.NOTE)


def _require_edit_permission(user: User, shared: SharedResource) -> None:
    if shared.owner_id == user.id:
        return
    if not shared.can_edit:
        raise SharePermissionDeniedError('This item was shared as view-only.')


def update_shared_task(user: User, family_id, shared_id, **fields):
    """Edits the underlying task of a shared-task record, on behalf of its
    owner, per PRD.md Section 6.4 ("delegate tasks to my children") —
    permitted when the requester is the task's owner or has been granted
    edit access via SharedResource.can_edit."""
    get_family(family_id)
    _get_membership_or_raise(user, family_id)
    shared = _get_shared_resource_or_raise(family_id, shared_id, SharedResourceType.TASK)
    _require_edit_permission(user, shared)

    from apps.tasks.services import TaskNotFoundError, update_task_for_user

    try:
        return update_task_for_user(shared.owner, shared.resource_id, **fields)
    except TaskNotFoundError as exc:
        raise ResourceNotFoundError(str(exc)) from exc


def complete_shared_task(user: User, family_id, shared_id):
    get_family(family_id)
    _get_membership_or_raise(user, family_id)
    shared = _get_shared_resource_or_raise(family_id, shared_id, SharedResourceType.TASK)
    _require_edit_permission(user, shared)

    from apps.tasks.services import TaskNotFoundError, complete_task_for_user

    try:
        return complete_task_for_user(shared.owner, shared.resource_id)
    except TaskNotFoundError as exc:
        raise ResourceNotFoundError(str(exc)) from exc


# --------------------------------------------------------------------------
# Housekeeping (ARCHITECTURE.md Section 8)
# --------------------------------------------------------------------------


def expire_stale_invitations() -> int:
    """Marks every pending invitation past its expires_at as EXPIRED.
    Returns the number of invitations expired. Invoked by the Celery Beat
    schedule in apps.family.tasks — a "housekeeping" background job, per
    ARCHITECTURE.md Section 8, mirroring the existing reminder-scan pattern
    in apps.notifications.tasks."""
    from apps.family.models import FamilyInvitation

    stale = FamilyInvitation.objects.filter(
        status=InvitationStatus.PENDING, expires_at__lt=timezone.now()
    )
    # Bulk .update() bypasses auto_now, so updated_at is set explicitly
    # (a recurring gotcha already documented for apps.notifications).
    count = stale.update(status=InvitationStatus.EXPIRED, updated_at=timezone.now())
    return count
