"""
Domain models — Accounts.

Custom User model, per ARCHITECTURE.md Section 5: MindMesh authenticates by
email (not username), and this same model backs both the email/password flow
and the Google OAuth flow.
"""

import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from apps.accounts.managers import UserManager


class AuthProvider(models.TextChoices):
    """How a user's account was originally created."""

    EMAIL = 'email', 'Email & Password'
    GOOGLE = 'google', 'Google OAuth'


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model, authenticated by email per ARCHITECTURE.md Section 5.

    Row-level ownership across the rest of the schema (ARCHITECTURE.md
    Section 4) is scoped to this model's primary key.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    full_name = models.CharField(max_length=255)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Google OAuth linkage. `google_sub` is Google's stable, unique subject
    # identifier for the account (the ID token's `sub` claim) — the correct
    # field to key off, since a user's Google email could theoretically
    # change. `auth_provider` records how the account originated so the
    # frontend/API can, e.g., avoid showing a password-change option for a
    # Google-only account that has no usable password.
    auth_provider = models.CharField(
        max_length=20, choices=AuthProvider.choices, default=AuthProvider.EMAIL
    )
    google_sub = models.CharField(max_length=255, unique=True, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        db_table = 'accounts_user'
        ordering = ['-created_at']
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __str__(self) -> str:
        return self.email


class ThemePreference(models.TextChoices):
    """Supported theme preferences, mirroring frontend/src/styles/theme.ts."""

    LIGHT = 'light', 'Light'
    DARK = 'dark', 'Dark'
    SYSTEM = 'system', 'Match System'


class UserSettings(models.Model):
    """
    Account-level preferences, per ROADMAP.md Milestone 2 ("Settings
    (account-level preferences)").

    Deliberately minimal at this stage: only preferences that already have a
    concrete consumer elsewhere in the codebase are included — theme ties
    into the existing Zustand `uiStore` (frontend/src/stores/uiStore.ts) and
    Tailwind dark-mode setup, and email notification opt-in is the natural
    account-level counterpart to the notification channels described in
    PRD.md Section 7. Further settings are added as the features that need
    them are built, rather than speculatively here.

    One-to-one with User rather than fields on User itself, so account
    identity/auth concerns and user preferences remain separately
    evolvable — a settings row can be added to or migrated independently of
    the auth-critical User table.
    """

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='settings', primary_key=True
    )
    theme_preference = models.CharField(
        max_length=10, choices=ThemePreference.choices, default=ThemePreference.SYSTEM
    )
    email_notifications_enabled = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'accounts_user_settings'
        verbose_name = 'user settings'
        verbose_name_plural = 'user settings'

    def __str__(self) -> str:
        return f'Settings for {self.user.email}'

