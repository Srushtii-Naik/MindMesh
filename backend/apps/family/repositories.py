"""
Repository / data-access layer — Family & Shared Workspace.

Encapsulates ORM queries for Family, FamilyMembership, FamilyInvitation,
EmergencyContact, and SharedResource, isolating persistence details from the
service layer, per ARCHITECTURE.md Section 3.
"""

from datetime import datetime

from django.db.models import QuerySet
from django.utils import timezone

from apps.accounts.models import User
from apps.family.models import (
    EmergencyContact,
    Family,
    FamilyInvitation,
    FamilyMembership,
    InvitationStatus,
    SharedResource,
)

# --------------------------------------------------------------------------
# Family
# --------------------------------------------------------------------------


def get_family_by_id(family_id) -> Family | None:
    return Family.objects.filter(id=family_id, is_active=True).first()


def create_family(*, name: str, created_by: User) -> Family:
    return Family.objects.create(name=name, created_by=created_by)


def update_family(family: Family, **fields) -> Family:
    for field, value in fields.items():
        setattr(family, field, value)
    family.save()
    return family


def soft_delete_family(family: Family) -> None:
    family.is_active = False
    family.deleted_at = timezone.now()
    family.save(update_fields=['is_active', 'deleted_at', 'updated_at'])


# --------------------------------------------------------------------------
# FamilyMembership
# --------------------------------------------------------------------------


def get_active_membership_for_user(user: User) -> FamilyMembership | None:
    """A user belongs to at most one active family at a time (Family's docstring)."""
    return (
        FamilyMembership.objects.filter(user=user, is_active=True)
        .select_related('family')
        .first()
    )


def get_membership_for_user_family(user: User, family_id) -> FamilyMembership | None:
    return FamilyMembership.objects.filter(
        user=user, family_id=family_id, is_active=True
    ).first()


def get_membership_by_id(family_id, membership_id) -> FamilyMembership | None:
    return FamilyMembership.objects.filter(
        id=membership_id, family_id=family_id, is_active=True
    ).select_related('user').first()


def list_active_memberships_for_family(family: Family) -> QuerySet[FamilyMembership]:
    return FamilyMembership.objects.filter(family=family, is_active=True).select_related('user')


def count_active_owners(family: Family) -> int:
    from apps.family.models import FamilyRole

    return FamilyMembership.objects.filter(
        family=family, is_active=True, role=FamilyRole.OWNER
    ).count()


def count_active_members(family: Family) -> int:
    return FamilyMembership.objects.filter(family=family, is_active=True).count()


def create_membership(*, family: Family, user: User, role: str) -> FamilyMembership:
    return FamilyMembership.objects.create(family=family, user=user, role=role)


def update_membership(membership: FamilyMembership, **fields) -> FamilyMembership:
    for field, value in fields.items():
        setattr(membership, field, value)
    membership.save()
    return membership


def deactivate_membership(membership: FamilyMembership) -> None:
    membership.is_active = False
    membership.removed_at = timezone.now()
    membership.save(update_fields=['is_active', 'removed_at', 'updated_at'])


# --------------------------------------------------------------------------
# FamilyInvitation
# --------------------------------------------------------------------------


def get_invitation_by_token(token) -> FamilyInvitation | None:
    return FamilyInvitation.objects.filter(token=token).select_related('family').first()


def get_invitation_for_family(family_id, invitation_id) -> FamilyInvitation | None:
    return FamilyInvitation.objects.filter(id=invitation_id, family_id=family_id).first()


def list_invitations_for_family(family: Family) -> QuerySet[FamilyInvitation]:
    return FamilyInvitation.objects.filter(family=family)


def list_pending_invitations_for_email(email: str) -> QuerySet[FamilyInvitation]:
    return FamilyInvitation.objects.filter(
        invited_email__iexact=email, status=InvitationStatus.PENDING
    ).select_related('family')


def has_pending_invitation(family: Family, email: str) -> bool:
    return FamilyInvitation.objects.filter(
        family=family, invited_email__iexact=email, status=InvitationStatus.PENDING
    ).exists()


def create_invitation(
    *, family: Family, invited_email: str, role: str, invited_by: User, expires_at: datetime
) -> FamilyInvitation:
    return FamilyInvitation.objects.create(
        family=family,
        invited_email=invited_email,
        role=role,
        invited_by=invited_by,
        expires_at=expires_at,
    )


def update_invitation(invitation: FamilyInvitation, **fields) -> FamilyInvitation:
    for field, value in fields.items():
        setattr(invitation, field, value)
    invitation.save()
    return invitation


# --------------------------------------------------------------------------
# EmergencyContact
# --------------------------------------------------------------------------


def list_emergency_contacts_for_family(family: Family) -> QuerySet[EmergencyContact]:
    return EmergencyContact.objects.filter(family=family, is_active=True)


def get_emergency_contact_for_family(family_id, contact_id) -> EmergencyContact | None:
    return EmergencyContact.objects.filter(
        id=contact_id, family_id=family_id, is_active=True
    ).first()


def create_emergency_contact(*, family: Family, added_by: User, **fields) -> EmergencyContact:
    return EmergencyContact.objects.create(family=family, added_by=added_by, **fields)


def update_emergency_contact(contact: EmergencyContact, **fields) -> EmergencyContact:
    for field, value in fields.items():
        setattr(contact, field, value)
    contact.save()
    return contact


def soft_delete_emergency_contact(contact: EmergencyContact) -> None:
    contact.is_active = False
    contact.deleted_at = timezone.now()
    contact.save(update_fields=['is_active', 'deleted_at', 'updated_at'])


# --------------------------------------------------------------------------
# SharedResource
# --------------------------------------------------------------------------


def list_shared_resources_for_family(
    family: Family, resource_type: str
) -> QuerySet[SharedResource]:
    return SharedResource.objects.filter(
        family=family, resource_type=resource_type, is_active=True
    ).select_related('owner', 'shared_by')


def get_shared_resource_for_family(family_id, shared_id) -> SharedResource | None:
    return (
        SharedResource.objects.filter(id=shared_id, family_id=family_id, is_active=True)
        .select_related('owner', 'shared_by')
        .first()
    )


def get_active_share_for_resource(
    family: Family, resource_type: str, resource_id
) -> SharedResource | None:
    return SharedResource.objects.filter(
        family=family, resource_type=resource_type, resource_id=resource_id, is_active=True
    ).first()


def create_shared_resource(
    *, family: Family, resource_type: str, resource_id, owner: User, shared_by: User, can_edit: bool
) -> SharedResource:
    return SharedResource.objects.create(
        family=family,
        resource_type=resource_type,
        resource_id=resource_id,
        owner=owner,
        shared_by=shared_by,
        can_edit=can_edit,
    )


def update_shared_resource(shared_resource: SharedResource, **fields) -> SharedResource:
    for field, value in fields.items():
        setattr(shared_resource, field, value)
    shared_resource.save()
    return shared_resource


def soft_delete_shared_resource(shared_resource: SharedResource) -> None:
    shared_resource.is_active = False
    shared_resource.deleted_at = timezone.now()
    shared_resource.save(update_fields=['is_active', 'deleted_at', 'updated_at'])
