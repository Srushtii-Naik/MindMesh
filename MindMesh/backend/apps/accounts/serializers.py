"""
DRF serializers — Accounts.

Handle request parsing/validation and response shaping only. Per
ARCHITECTURE.md Section 3, business logic (uniqueness enforcement, user
creation, token verification, etc.) lives in the service layer, not here.
"""

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.accounts.models import User, UserSettings


class UserPublicSerializer(serializers.ModelSerializer):
    """Minimal, non-sensitive user representation returned in auth responses."""

    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'created_at']
        read_only_fields = fields


class RegisterSerializer(serializers.Serializer):
    """
    Validates registration input.

    Intentionally a plain Serializer (not ModelSerializer) — user creation
    involves password hashing and a domain uniqueness rule, so object
    creation is delegated to apps.accounts.services.register_user rather
    than an auto-generated .create().
    """

    email = serializers.EmailField()
    full_name = serializers.CharField(max_length=255, trim_whitespace=True)
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    def validate_email(self, value: str) -> str:
        return value.lower().strip()

    def validate_full_name(self, value: str) -> str:
        if not value.strip():
            raise serializers.ValidationError('Full name cannot be blank.')
        return value.strip()

    def validate_password(self, value: str) -> str:
        # Enforces AUTH_PASSWORD_VALIDATORS (config/settings/base.py), including
        # minimum length, similarity, common-password, and numeric-only checks.
        validate_password(value)
        return value

    def validate(self, attrs: dict) -> dict:
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError(
                {'password_confirm': 'Passwords do not match.'}
            )
        return attrs


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Login serializer.

    simple-jwt's TokenObtainPairSerializer already uses the model's
    USERNAME_FIELD (email, per apps.accounts.models.User) as the login
    identifier. This override additionally attaches the public user
    representation to the token response so the frontend doesn't need a
    separate request to know who just logged in.
    """

    def validate(self, attrs: dict) -> dict:
        data = super().validate(attrs)
        data['user'] = UserPublicSerializer(self.user).data
        return data


class GoogleAuthSerializer(serializers.Serializer):
    """
    Validates the Google Identity Services credential handed to us by the
    frontend. Verification of the token itself (signature, audience,
    expiry) happens in the service layer against Google's servers — this
    serializer only confirms the shape of the request.
    """

    id_token = serializers.CharField(write_only=True, allow_blank=False)


class PasswordResetRequestSerializer(serializers.Serializer):
    """Validates a 'forgot password' request."""

    email = serializers.EmailField()

    def validate_email(self, value: str) -> str:
        return value.lower().strip()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Validates the token/new-password pair submitted from the reset-password page."""

    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)
    new_password_confirm = serializers.CharField(write_only=True)

    def validate_new_password(self, value: str) -> str:
        validate_password(value)
        return value

    def validate(self, attrs: dict) -> dict:
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError(
                {'new_password_confirm': 'Passwords do not match.'}
            )
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Full profile representation for the authenticated user (GET /auth/me/).

    Email is intentionally read-only here: changing the email a user
    authenticates with is a re-verification-worthy action (and, for Google
    accounts, tied to the linked Google identity) that is out of scope for
    this milestone's Profile feature — see PROJECT_RULES.md Section 1 on
    not building ahead of a defined need.
    """

    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'auth_provider', 'created_at', 'updated_at']
        read_only_fields = ['id', 'email', 'auth_provider', 'created_at', 'updated_at']


class UserProfileUpdateSerializer(serializers.Serializer):
    """Validates the editable subset of a user's profile (PATCH /auth/me/)."""

    full_name = serializers.CharField(max_length=255, trim_whitespace=True)

    def validate_full_name(self, value: str) -> str:
        if not value.strip():
            raise serializers.ValidationError('Full name cannot be blank.')
        return value.strip()


class UserSettingsSerializer(serializers.ModelSerializer):
    """Account-level preferences (GET/PATCH /auth/settings/)."""

    class Meta:
        model = UserSettings
        fields = ['theme_preference', 'email_notifications_enabled', 'updated_at']
        read_only_fields = ['updated_at']


class SessionSerializer(serializers.Serializer):
    """
    Represents one active session (an outstanding, non-blacklisted refresh
    token) for the session-management endpoints.
    """

    id = serializers.IntegerField()
    created_at = serializers.DateTimeField()
    expires_at = serializers.DateTimeField()
