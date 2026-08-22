"""
Repository / data-access layer — Accounts.

Encapsulates ORM queries for the User and UserSettings models, isolating
persistence details from the service layer, per ARCHITECTURE.md Section 3.
"""

from django.utils import timezone
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

from apps.accounts.models import AuthProvider, User, UserSettings


# --------------------------------------------------------------------------
# User
# --------------------------------------------------------------------------

def create_user(*, email: str, password: str, full_name: str) -> User:
    """Create and persist a new user with a hashed password."""
    return User.objects.create_user(email=email, password=password, full_name=full_name)


def create_google_user(*, email: str, full_name: str, google_sub: str) -> User:
    """
    Create a user provisioned via Google OAuth.

    No usable password is set — `set_unusable_password()` matches Django's
    own convention for accounts that don't authenticate via password, and
    keeps `has_usable_password()` accurate for any future "can this account
    set a password" UI decision.
    """
    user = User(
        email=email,
        full_name=full_name,
        google_sub=google_sub,
        auth_provider=AuthProvider.GOOGLE,
    )
    user.set_unusable_password()
    user.save()
    return user


def get_user_by_email(email: str) -> User | None:
    """Return the user with the given email (case-insensitive), or None."""
    return User.objects.filter(email__iexact=email).first()


def get_user_by_google_sub(google_sub: str) -> User | None:
    """Return the user linked to the given Google subject ID, or None."""
    return User.objects.filter(google_sub=google_sub).first()


def get_user_by_id(user_id) -> User | None:
    """Return the user with the given primary key, or None."""
    return User.objects.filter(id=user_id).first()


def email_exists(email: str) -> bool:
    """Return whether a user with the given email already exists."""
    return User.objects.filter(email__iexact=email).exists()


def update_user_full_name(user: User, full_name: str) -> User:
    """Persist a change to the user's display name."""
    user.full_name = full_name
    user.save(update_fields=['full_name', 'updated_at'])
    return user


def set_user_password(user: User, password: str) -> User:
    """Hash and persist a new password for the user."""
    user.set_password(password)
    user.save(update_fields=['password', 'updated_at'])
    return user


# --------------------------------------------------------------------------
# UserSettings
# --------------------------------------------------------------------------

def get_or_create_settings(user: User) -> UserSettings:
    """Return the user's settings row, creating a default one if absent."""
    settings, _ = UserSettings.objects.get_or_create(user=user)
    return settings


def update_settings(settings: UserSettings, **fields) -> UserSettings:
    """Persist a partial update to a settings row."""
    for field, value in fields.items():
        setattr(settings, field, value)
    settings.save()
    return settings


# --------------------------------------------------------------------------
# Sessions (simple-jwt OutstandingToken / BlacklistedToken)
# --------------------------------------------------------------------------

def list_active_sessions_for_user(user: User):
    """
    Return outstanding (issued, not-yet-blacklisted, not-yet-expired) refresh
    tokens for the user — each represents a device/browser session that can
    still be used to obtain new access tokens.
    """
    blacklisted_ids = BlacklistedToken.objects.filter(
        token__user=user
    ).values_list('token_id', flat=True)

    return (
        OutstandingToken.objects.filter(user=user, expires_at__gt=timezone.now())
        .exclude(id__in=blacklisted_ids)
        .order_by('-created_at')
    )


def get_outstanding_token_for_user(user: User, token_id) -> OutstandingToken | None:
    """Return a specific outstanding token owned by the user, or None."""
    return OutstandingToken.objects.filter(id=token_id, user=user).first()


def blacklist_outstanding_token(token: OutstandingToken) -> None:
    """Blacklist a single outstanding token, revoking that session."""
    BlacklistedToken.objects.get_or_create(token=token)


def blacklist_all_outstanding_tokens_for_user(user: User) -> None:
    """
    Blacklist every outstanding, non-expired refresh token for the user.

    Shared by both the password-reset-confirm flow (force re-login
    everywhere after a credential change) and the "sign out of all devices"
    session-management action — a single implementation, per the
    do-not-duplicate-authentication-logic requirement.
    """
    for token in OutstandingToken.objects.filter(user=user, expires_at__gt=timezone.now()):
        BlacklistedToken.objects.get_or_create(token=token)
