"""
DRF views — Accounts.

Handles HTTP concerns only (request parsing, status codes, response shaping).
Business logic is delegated to apps.accounts.services, per ARCHITECTURE.md
Section 3.
"""

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.accounts.serializers import (
    EmailTokenObtainPairSerializer,
    GoogleAuthSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RegisterSerializer,
    SessionSerializer,
    UserPublicSerializer,
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    UserSettingsSerializer,
)
from apps.accounts.services import (
    EmailAlreadyRegisteredError,
    GoogleAccountEmailConflictError,
    InvalidGoogleTokenError,
    InvalidPasswordResetTokenError,
    SessionNotFoundError,
    authenticate_or_create_google_user,
    confirm_password_reset,
    get_settings_for_user,
    issue_tokens_for_user,
    list_sessions,
    register_user,
    request_password_reset,
    revoke_all_sessions,
    revoke_session,
    update_profile,
    update_settings_for_user,
)


class RegisterView(APIView):
    """
    POST /api/v1/auth/register/

    Creates a new account and immediately issues a token pair, matching the
    registration flow described in ARCHITECTURE.md Section 5 ("On success,
    backend issues an access token and a refresh token").
    """

    permission_classes = [AllowAny]
    throttle_scope = 'auth_register'

    def post(self, request: Request) -> Response:
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        try:
            user = register_user(
                email=validated['email'],
                password=validated['password'],
                full_name=validated['full_name'],
            )
        except EmailAlreadyRegisteredError as exc:
            return Response(
                {'detail': str(exc), 'code': 'email_already_registered'},
                status=status.HTTP_409_CONFLICT,
            )

        tokens = issue_tokens_for_user(user)
        return Response(
            {'user': UserPublicSerializer(user).data, **tokens},
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    """
    POST /api/v1/auth/login/

    Email/password login. Delegates credential verification to simple-jwt's
    TokenObtainPairView, with EmailTokenObtainPairSerializer attaching the
    public user representation to the response.
    """

    permission_classes = [AllowAny]
    serializer_class = EmailTokenObtainPairSerializer
    throttle_scope = 'auth_login'


class TokenRefreshThrottledView(TokenRefreshView):
    """
    POST /api/v1/auth/token/refresh/

    Thin subclass of simple-jwt's TokenRefreshView that adds rate limiting
    (PROJECT_RULES.md Section 8) without altering any refresh behavior —
    simple-jwt's own view already handles rotation/blacklisting per
    ARCHITECTURE.md Section 5.
    """

    throttle_scope = 'auth_token_refresh'


class LogoutView(APIView):
    """
    POST /api/v1/auth/logout/

    Blacklists the supplied refresh token so it can no longer be used to
    obtain new access tokens. Requires a valid access token — only an
    authenticated session can log itself out.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'detail': 'Refresh token is required.', 'code': 'refresh_required'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response(
                {'detail': 'Refresh token is invalid or already expired.', 'code': 'invalid_token'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)


class GoogleLoginView(APIView):
    """
    POST /api/v1/auth/google/

    Accepts a Google Identity Services ID token, verifies it against
    Google, and issues the same internal JWT pair as email/password login —
    per ARCHITECTURE.md Section 5, Google OAuth is an alternate entry point
    into the same session model, not a separate authentication system.
    """

    permission_classes = [AllowAny]
    throttle_scope = 'auth_google'

    def post(self, request: Request) -> Response:
        serializer = GoogleAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = authenticate_or_create_google_user(serializer.validated_data['id_token'])
        except InvalidGoogleTokenError as exc:
            return Response(
                {'detail': str(exc), 'code': 'invalid_google_token'},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except GoogleAccountEmailConflictError as exc:
            return Response(
                {'detail': str(exc), 'code': 'email_already_registered'},
                status=status.HTTP_409_CONFLICT,
            )

        tokens = issue_tokens_for_user(user)
        return Response({'user': UserPublicSerializer(user).data, **tokens}, status=status.HTTP_200_OK)


class PasswordResetRequestView(APIView):
    """
    POST /api/v1/auth/password-reset/

    Always returns a generic 200 response, whether or not the email is
    registered, to avoid leaking account existence (account enumeration).
    """

    permission_classes = [AllowAny]
    throttle_scope = 'auth_password_reset'

    def post(self, request: Request) -> Response:
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        request_password_reset(serializer.validated_data['email'])

        return Response(
            {'detail': 'If an account exists for this email, a reset link has been sent.'},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(APIView):
    """
    POST /api/v1/auth/password-reset/confirm/

    Sets a new password given a valid uid/token pair, and invalidates every
    existing session for the user as a precaution.
    """

    permission_classes = [AllowAny]
    throttle_scope = 'auth_password_reset_confirm'

    def post(self, request: Request) -> Response:
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        try:
            confirm_password_reset(
                uidb64=validated['uid'],
                token=validated['token'],
                new_password=validated['new_password'],
            )
        except InvalidPasswordResetTokenError as exc:
            return Response(
                {'detail': str(exc), 'code': 'invalid_reset_token'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {'detail': 'Password has been reset. Please sign in again.'},
            status=status.HTTP_200_OK,
        )


class ProfileView(APIView):
    """
    GET  /api/v1/auth/me/  — return the authenticated user's profile.
    PATCH /api/v1/auth/me/ — update the editable subset of the profile.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        return Response(UserProfileSerializer(request.user).data)

    def patch(self, request: Request) -> Response:
        serializer = UserProfileUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        user = update_profile(request.user, full_name=serializer.validated_data['full_name'])
        return Response(UserProfileSerializer(user).data)


class SettingsView(APIView):
    """
    GET   /api/v1/auth/settings/ — return the authenticated user's account settings.
    PATCH /api/v1/auth/settings/ — update one or more settings.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        return Response(UserSettingsSerializer(get_settings_for_user(request.user)).data)

    def patch(self, request: Request) -> Response:
        serializer = UserSettingsSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        settings_obj = update_settings_for_user(request.user, **serializer.validated_data)
        return Response(UserSettingsSerializer(settings_obj).data)


class SessionListView(APIView):
    """
    GET /api/v1/auth/sessions/

    Lists the authenticated user's active sessions (devices/browsers that
    currently hold a usable refresh token), per PRD.md Section 14 —
    "Session management with device-level visibility and remote sign-out
    capability." Device metadata (user-agent/IP) is not currently captured
    at token-issuance time, so sessions are identified by issue/expiry time
    only; see inline note on `apps/accounts/repositories.py` for the scoping
    rationale.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        sessions = list_sessions(request.user)
        return Response(SessionSerializer(sessions, many=True).data)


class SessionRevokeView(APIView):
    """POST /api/v1/auth/sessions/<id>/revoke/ — sign out a single session."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request, session_id: int) -> Response:
        try:
            revoke_session(request.user, session_id)
        except SessionNotFoundError as exc:
            return Response(
                {'detail': str(exc), 'code': 'session_not_found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class SessionRevokeAllView(APIView):
    """POST /api/v1/auth/sessions/revoke-all/ — sign out of every device."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        revoke_all_sessions(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
