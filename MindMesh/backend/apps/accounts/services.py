"""
Service layer — Accounts.

Domain business logic for registration, login session issuance, Google
OAuth, password reset, profile/settings management, and session management.
Per ARCHITECTURE.md Section 3: views call services; services never import DRF.
"""

from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.db import IntegrityError, transaction
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User, UserSettings
from apps.accounts.repositories import (
    blacklist_all_outstanding_tokens_for_user,
    blacklist_outstanding_token,
    create_google_user,
    create_user,
    email_exists,
    get_or_create_settings,
    get_outstanding_token_for_user,
    get_user_by_email,
    get_user_by_google_sub,
    get_user_by_id,
    list_active_sessions_for_user,
    set_user_password,
    update_settings,
    update_user_full_name,
)


class EmailAlreadyRegisteredError(Exception):
    """Raised when attempting to register an email that's already in use."""


class InvalidGoogleTokenError(Exception):
    """Raised when a Google ID token fails verification."""


class GoogleAccountEmailConflictError(Exception):
    """Raised when a Google account's email already belongs to a non-Google account."""


class InvalidPasswordResetTokenError(Exception):
    """Raised when a password reset token/uid pair is invalid or expired."""


class SessionNotFoundError(Exception):
    """Raised when a session (outstanding refresh token) cannot be found for the user."""


# --------------------------------------------------------------------------
# Registration & login (existing — untouched)
# --------------------------------------------------------------------------

def register_user(*, email: str, password: str, full_name: str) -> User:
    """
    Register a new user.

    Password strength is validated at the serializer layer (API layer
    concern); this service enforces the domain rule that emails are unique,
    independent of how the request arrived.

    The existence check and the insert are not atomic on their own, so two
    concurrent requests for the same email could both pass the check before
    either commits. The IntegrityError catch below is the authoritative
    guard against that race — the unique constraint on User.email is the
    real source of truth; the upfront check just gives the common case a
    clean, expected error rather than a raw database error.
    """
    if email_exists(email):
        raise EmailAlreadyRegisteredError('A user with this email already exists.')

    try:
        with transaction.atomic():
            user = create_user(email=email, password=password, full_name=full_name)
            get_or_create_settings(user)
            return user
    except IntegrityError as exc:
        raise EmailAlreadyRegisteredError('A user with this email already exists.') from exc


def issue_tokens_for_user(user: User) -> dict[str, str]:
    """Issue a fresh JWT access/refresh pair for a user (ARCHITECTURE.md Section 5)."""
    refresh = RefreshToken.for_user(user)
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }


# --------------------------------------------------------------------------
# Google OAuth
# --------------------------------------------------------------------------

def authenticate_or_create_google_user(id_token_value: str) -> User:
    """
    Verify a Google ID token and return the matching MindMesh user,
    creating one on first sign-in.

    Reuses the same User model and `issue_tokens_for_user` as email/password
    auth — Google sign-in is an alternate way to *establish* a session, not
    a parallel authentication system.
    """
    client_id = settings.GOOGLE_OAUTH_CLIENT_ID
    if not client_id:
        raise InvalidGoogleTokenError('Google OAuth is not configured on this server.')

    try:
        claims = google_id_token.verify_oauth2_token(
            id_token_value, google_requests.Request(), client_id
        )
    except ValueError as exc:
        raise InvalidGoogleTokenError('Google ID token is invalid or expired.') from exc

    google_sub = claims.get('sub')
    email = claims.get('email')
    email_verified = claims.get('email_verified', False)
    full_name = claims.get('name') or (email.split('@')[0] if email else 'MindMesh User')

    if not google_sub or not email:
        raise InvalidGoogleTokenError('Google token did not include the expected claims.')
    if not email_verified:
        raise InvalidGoogleTokenError('Google account email is not verified.')

    existing_by_sub = get_user_by_google_sub(google_sub)
    if existing_by_sub:
        return existing_by_sub

    existing_by_email = get_user_by_email(email)
    if existing_by_email:
        # An email/password account already owns this email. Per
        # PROJECT_RULES.md Section 8 (security-first), we do not silently
        # attach a Google identity to an existing account without the user
        # having proven ownership through that account's own credentials —
        # doing so would let an attacker who controls a Google account with
        # a matching (e.g. spoofed-at-signup) email take over an unrelated
        # MindMesh account.
        raise GoogleAccountEmailConflictError(
            'An account with this email already exists. Sign in with your password instead.'
        )

    with transaction.atomic():
        user = create_google_user(email=email, full_name=full_name, google_sub=google_sub)
        get_or_create_settings(user)
        return user


# --------------------------------------------------------------------------
# Password reset
# --------------------------------------------------------------------------

_password_reset_token_generator = PasswordResetTokenGenerator()


def build_password_reset_link(user: User) -> str:
    """
    Build the uid/token pair and full frontend URL for a password reset
    email, using Django's own `PasswordResetTokenGenerator` — the same
    battle-tested, time-limited, single-use-until-password-changes token
    scheme Django's built-in auth views use, applied here to our custom
    user model and DRF endpoints instead of Django's HTML views.
    """
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = _password_reset_token_generator.make_token(user)
    frontend_url = settings.FRONTEND_URL.rstrip('/')
    return f'{frontend_url}/reset-password?uid={uidb64}&token={token}'


def request_password_reset(email: str) -> None:
    """
    Kick off a password reset for the given email, if an account exists.

    Deliberately does not report whether the email exists — the view layer
    always returns the same generic response, to avoid account enumeration.
    """
    user = get_user_by_email(email)
    if user is None or not user.is_active:
        return

    # Imported locally to avoid a hard import-time dependency between the
    # service layer and Celery task registration.
    from apps.accounts.tasks import send_password_reset_email

    reset_link = build_password_reset_link(user)
    send_password_reset_email.delay(user_id=str(user.pk), reset_link=reset_link)


def confirm_password_reset(*, uidb64: str, token: str, new_password: str) -> User:
    """
    Validate a reset token and set the new password.

    All of the user's outstanding sessions are blacklisted afterward — a
    password reset is a strong signal the previous credential may have been
    compromised, so every existing refresh token (this device and any
    other) is invalidated, reusing the same helper session-management uses
    for "sign out everywhere".
    """
    try:
        user_id = force_str(urlsafe_base64_decode(uidb64))
        user = get_user_by_id(user_id)
    except (TypeError, ValueError, OverflowError):
        user = None

    if user is None or not _password_reset_token_generator.check_token(user, token):
        raise InvalidPasswordResetTokenError('This password reset link is invalid or has expired.')

    set_user_password(user, new_password)
    blacklist_all_outstanding_tokens_for_user(user)
    return user


# --------------------------------------------------------------------------
# Profile
# --------------------------------------------------------------------------

def update_profile(user: User, *, full_name: str) -> User:
    """Update the editable portion of a user's profile."""
    return update_user_full_name(user, full_name)


# --------------------------------------------------------------------------
# Settings
# --------------------------------------------------------------------------

def get_settings_for_user(user: User) -> UserSettings:
    return get_or_create_settings(user)


def update_settings_for_user(user: User, **fields) -> UserSettings:
    current = get_or_create_settings(user)
    return update_settings(current, **fields)


# --------------------------------------------------------------------------
# Session management
# --------------------------------------------------------------------------

def list_sessions(user: User) -> list[OutstandingToken]:
    return list(list_active_sessions_for_user(user))


def revoke_session(user: User, session_id) -> None:
    """Revoke a single session (outstanding refresh token) owned by the user."""
    token = get_outstanding_token_for_user(user, session_id)
    if token is None:
        raise SessionNotFoundError('Session not found.')
    blacklist_outstanding_token(token)


def revoke_all_sessions(user: User) -> None:
    """Revoke every active session for the user (sign out of all devices)."""
    blacklist_all_outstanding_tokens_for_user(user)
