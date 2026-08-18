"""
Domain models — Family & Shared Workspace.

Per ROADMAP.md Milestone 10: family member invitation/management, shared
tasks/calendar/notes, and emergency contacts. Per ARCHITECTURE.md Section 4,
every domain table is scoped appropriately and timestamps are standardized;
per PROJECT_RULES.md Section 7, user-generated content (Family,
EmergencyContact, SharedResource) uses soft deletes.

`SharedResource` deliberately does NOT hold a foreign key to Task/Event/Note.
Per ARCHITECTURE.md Section 3 ("cross-domain communication happens through
service interfaces, not direct model imports across apps"), it instead
stores a `resource_type` + `resource_id` pair and is resolved at the service
layer by calling into apps.tasks.services / apps.calendar_events.services /
apps.notes.services — the same pattern apps.calendar_events.services already
uses to read task due dates without importing apps.tasks.models.
"""

import uuid

from django.conf import settings
from django.db import models
from django.db.models import Q


class FamilyRole(models.TextChoices):
    """
    A member's role within a family.

    Per PRD.md Section 6.4/6.1 (parent oversight of a child's profile):
    OWNER and ADULT can manage membership, invitations, and emergency
    contacts; CHILD is a participant with a restricted management surface,
    enforced at the service layer (never just the API layer, per
    ARCHITECTURE.md Section 10).
    """

    OWNER = 'owner', 'Owner'
    ADULT = 'adult', 'Adult'
    CHILD = 'child', 'Child'


class InvitationStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    ACCEPTED = 'accepted', 'Accepted'
    DECLINED = 'declined', 'Declined'
    CANCELED = 'canceled', 'Canceled'
    EXPIRED = 'expired', 'Expired'


class SharedResourceType(models.TextChoices):
    """Which domain a SharedResource's resource_id points into."""

    TASK = 'task', 'Task'
    EVENT = 'event', 'Event'
    NOTE = 'note', 'Note'


class Family(models.Model):
    """
    A household/family group (ROADMAP.md Milestone 10: "Family members
    (invite/manage)"). A user belongs to at most one active family at a
    time (enforced at the service layer) — matching PRD.md's "household"
    framing rather than allowing unbounded overlapping family graphs.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='families_created',
    )

    # Soft delete (PROJECT_RULES.md Section 7).
    is_active = models.BooleanField(default=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'family_family'
        ordering = ['-created_at']
        verbose_name = 'family'
        verbose_name_plural = 'families'

    def __str__(self) -> str:
        return self.name


class FamilyMembership(models.Model):
    """
    Links a user to a family with a role. Soft-removed (is_active=False)
    rather than hard-deleted on removal/leave, to preserve an audit trail
    per PROJECT_RULES.md Section 7 — a partial unique index (via `condition`)
    still allows the same user to rejoin later without a stale-row conflict.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='family_memberships'
    )
    role = models.CharField(max_length=10, choices=FamilyRole.choices, default=FamilyRole.ADULT)

    is_active = models.BooleanField(default=True)
    removed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'family_membership'
        ordering = ['role', 'created_at']
        verbose_name = 'family membership'
        verbose_name_plural = 'family memberships'
        constraints = [
            models.UniqueConstraint(
                fields=['family', 'user'],
                condition=Q(is_active=True),
                name='unique_active_membership_per_family_user',
            )
        ]
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['family', 'is_active']),
        ]

    def __str__(self) -> str:
        return f'{self.user_id} in {self.family_id} ({self.role})'


class FamilyInvitation(models.Model):
    """
    An invitation for someone to join a family (ROADMAP.md Milestone 10:
    "invite/manage"). Invited by email rather than by user id, since the
    invitee may not have a MindMesh account yet — `token` is what the
    accept/decline links are keyed on.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='invitations')
    invited_email = models.EmailField()
    role = models.CharField(max_length=10, choices=FamilyRole.choices, default=FamilyRole.ADULT)
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_family_invitations'
    )
    status = models.CharField(
        max_length=10, choices=InvitationStatus.choices, default=InvitationStatus.PENDING
    )
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    expires_at = models.DateTimeField()
    responded_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'family_invitation'
        ordering = ['-created_at']
        verbose_name = 'family invitation'
        verbose_name_plural = 'family invitations'
        indexes = [
            models.Index(fields=['family', 'status']),
            models.Index(fields=['invited_email', 'status']),
        ]

    def __str__(self) -> str:
        return f'{self.invited_email} -> {self.family_id} ({self.status})'


class EmergencyContact(models.Model):
    """A contact visible to every active member of a family (ROADMAP.md
    Milestone 10: "Emergency contacts")."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    family = models.ForeignKey(
        Family, on_delete=models.CASCADE, related_name='emergency_contacts'
    )
    name = models.CharField(max_length=255)
    relationship = models.CharField(max_length=100, blank=True, default='')
    phone_number = models.CharField(max_length=30)
    email = models.EmailField(blank=True, default='')
    notes = models.TextField(blank=True, default='')
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='emergency_contacts_added',
    )

    # Soft delete (PROJECT_RULES.md Section 7).
    is_active = models.BooleanField(default=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'family_emergency_contact'
        ordering = ['name']
        verbose_name = 'emergency contact'
        verbose_name_plural = 'emergency contacts'
        indexes = [models.Index(fields=['family', 'is_active'])]

    def __str__(self) -> str:
        return self.name


class SharedResource(models.Model):
    """
    Marks a single task/event/note as shared with a family. See module
    docstring for why this is a (resource_type, resource_id) pair rather
    than a direct foreign key into another domain's models.

    `owner` is who actually owns the underlying resource (its `user` field
    in apps.tasks/apps.calendar_events/apps.notes); `shared_by` is who
    performed the share action — normally the same person, but kept
    separate since it's conceptually a different fact.

    `can_edit` implements the "configurable permissions" PRD.md Section 13
    calls for: False (the default) means family members can only view the
    shared resource; True lets other members edit it — the delegation model
    PRD.md Section 6.4 describes ("delegate tasks to my children").
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    family = models.ForeignKey(
        Family, on_delete=models.CASCADE, related_name='shared_resources'
    )
    resource_type = models.CharField(max_length=10, choices=SharedResourceType.choices)
    resource_id = models.UUIDField()
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shared_resources_owned'
    )
    shared_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='shared_resources_shared',
    )
    can_edit = models.BooleanField(default=False)

    # Soft delete (PROJECT_RULES.md Section 7) — "unsharing" deactivates
    # the share record rather than deleting history of it having existed.
    is_active = models.BooleanField(default=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'family_shared_resource'
        ordering = ['-created_at']
        verbose_name = 'shared resource'
        verbose_name_plural = 'shared resources'
        constraints = [
            models.UniqueConstraint(
                fields=['family', 'resource_type', 'resource_id'],
                condition=Q(is_active=True),
                name='unique_active_share_per_family_resource',
            )
        ]
        indexes = [
            models.Index(fields=['family', 'resource_type', 'is_active']),
            models.Index(fields=['owner', 'resource_type']),
        ]

    def __str__(self) -> str:
        return f'{self.resource_type}:{self.resource_id} shared in {self.family_id}'
