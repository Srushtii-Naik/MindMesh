"""
URL routes — Accounts.

Mounted at /api/v1/auth/ from config/urls.py, per ARCHITECTURE.md Section 6
API versioning convention.
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.accounts.views import (
    GoogleLoginView,
    LoginView,
    LogoutView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    ProfileView,
    RegisterView,
    SessionListView,
    SessionRevokeAllView,
    SessionRevokeView,
    SettingsView,
)

urlpatterns = [
    # Core authentication (Milestone 2.1)
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('login/', LoginView.as_view(), name='auth-login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='auth-token-refresh'),
    path('logout/', LogoutView.as_view(), name='auth-logout'),

    # Google OAuth
    path('google/', GoogleLoginView.as_view(), name='auth-google'),

    # Password reset
    path('password-reset/', PasswordResetRequestView.as_view(), name='auth-password-reset'),
    path(
        'password-reset/confirm/',
        PasswordResetConfirmView.as_view(),
        name='auth-password-reset-confirm',
    ),

    # Profile
    path('me/', ProfileView.as_view(), name='auth-profile'),

    # Settings
    path('settings/', SettingsView.as_view(), name='auth-settings'),

    # Session management
    path('sessions/', SessionListView.as_view(), name='auth-sessions'),
    path('sessions/<int:session_id>/revoke/', SessionRevokeView.as_view(), name='auth-session-revoke'),
    path('sessions/revoke-all/', SessionRevokeAllView.as_view(), name='auth-sessions-revoke-all'),
]
