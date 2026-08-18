"""
DRF serializers — Family & Shared Workspace.

Handle request parsing/validation and response shaping only. Per
ARCHITECTURE.md Section 3, ownership/permission checks and cross-domain
resolution live in the service layer, not here.
"""

from rest_framework import serializers

from apps.calendar_events.serializers import EventSerializer
from apps.family.models import (
    EmergencyContact,
    Family,
    FamilyInvitation,
    FamilyMembership,
    FamilyRole,
    SharedResource,
)
from apps.notes.serializers import NoteSerializer
from apps.tasks.serializers import TaskSerializer

# --------------------------------------------------------------------------
# Family
# --------------------------------------------------------------------------


class FamilySerializer(serializers.ModelSerializer):
    class Meta:
        model = Family
        fields = ['id', 'name', 'created_by', 'created_at', 'updated_at']
        read_only_fields = fields


class FamilyWriteSerializer(serializers.Serializer):
    """Validates create/update input for a family."""

    name = serializers.CharField(max_length=255, trim_whitespace=True, required=False)

    def validate_name(self, value: str) -> str:
        if not value.strip():
            raise serializers.ValidationError('Family name cannot be blank.')
        return value.strip()

    def validate(self, attrs: dict) -> dict:
        if not self.partial and 'name' not in attrs:
            raise serializers.ValidationError({'name': 'This field is required.'})
        return attrs


# --------------------------------------------------------------------------
# Membership
# --------------------------------------------------------------------------


class MemberUserSerializer(serializers.Serializer):
    """Minimal, non-sensitive user representation for member listings."""

    id = serializers.UUIDField()
    email = serializers.EmailField()
    full_name = serializers.CharField()


class FamilyMembershipSerializer(serializers.ModelSerializer):
    user = MemberUserSerializer(read_only=True)

    class Meta:
        model = FamilyMembership
        fields = ['id', 'user', 'role', 'created_at']
        read_only_fields = fields


class MemberRoleWriteSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=FamilyRole.choices)


# --------------------------------------------------------------------------
# Invitations
# --------------------------------------------------------------------------


class FamilyInvitationSerializer(serializers.ModelSerializer):
    invited_by = MemberUserSerializer(read_only=True)
    family = FamilySerializer(read_only=True)

    class Meta:
        model = FamilyInvitation
        fields = [
            'id', 'family', 'invited_email', 'role', 'invited_by', 'status',
            'expires_at', 'responded_at', 'created_at',
        ]
        read_only_fields = fields


class InviteMemberWriteSerializer(serializers.Serializer):
    """`role` excludes OWNER — see services.invite_member for why."""

    email = serializers.EmailField()
    role = serializers.ChoiceField(
        choices=[FamilyRole.ADULT, FamilyRole.CHILD], default=FamilyRole.ADULT
    )


# --------------------------------------------------------------------------
# Emergency contacts
# --------------------------------------------------------------------------


class EmergencyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyContact
        fields = [
            'id', 'name', 'relationship', 'phone_number', 'email', 'notes',
            'added_by', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'added_by', 'created_at', 'updated_at']


class EmergencyContactWriteSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, trim_whitespace=True, required=False)
    relationship = serializers.CharField(max_length=100, allow_blank=True, required=False)
    phone_number = serializers.CharField(max_length=30, required=False)
    email = serializers.EmailField(allow_blank=True, required=False)
    notes = serializers.CharField(allow_blank=True, required=False)

    def validate_name(self, value: str) -> str:
        if not value.strip():
            raise serializers.ValidationError('Name cannot be blank.')
        return value.strip()

    def validate_phone_number(self, value: str) -> str:
        if not value.strip():
            raise serializers.ValidationError('Phone number cannot be blank.')
        return value.strip()

    def validate(self, attrs: dict) -> dict:
        if not self.partial:
            for required in ('name', 'phone_number'):
                if required not in attrs:
                    raise serializers.ValidationError({required: 'This field is required.'})
        return attrs


# --------------------------------------------------------------------------
# Shared resources
# --------------------------------------------------------------------------


class ShareResourceWriteSerializer(serializers.Serializer):
    resource_id = serializers.UUIDField()
    can_edit = serializers.BooleanField(default=False)


class SharePermissionWriteSerializer(serializers.Serializer):
    can_edit = serializers.BooleanField()


class SharedResourceMetaSerializer(serializers.ModelSerializer):
    """The SharedResource record itself (who shared it, with whom, and
    with what permission) — nested alongside the resolved resource in list
    responses (see views.py)."""

    owner = MemberUserSerializer(read_only=True)
    shared_by = MemberUserSerializer(read_only=True)

    class Meta:
        model = SharedResource
        fields = ['id', 'resource_type', 'owner', 'shared_by', 'can_edit', 'created_at']
        read_only_fields = fields


class SharedTaskSerializer(serializers.Serializer):
    share = SharedResourceMetaSerializer()
    task = TaskSerializer(source='resource')


class SharedEventSerializer(serializers.Serializer):
    share = SharedResourceMetaSerializer()
    event = EventSerializer(source='resource')


class SharedNoteSerializer(serializers.Serializer):
    share = SharedResourceMetaSerializer()
    note = NoteSerializer(source='resource')
