/**
 * Auth feature types.
 * Mirrors the backend contract exposed under /api/v1/auth/ (apps/accounts/serializers.py).
 */

export interface AuthUser {
  id: string;
  email: string;
  full_name: string;
  created_at: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface AuthResponse extends AuthTokens {
  user: AuthUser;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload {
  email: string;
  full_name: string;
  password: string;
  password_confirm: string;
}

export interface RefreshResponse {
  access: string;
  refresh?: string;
}

export interface GoogleAuthPayload {
  id_token: string;
}

export interface PasswordResetRequestPayload {
  email: string;
}

export interface PasswordResetConfirmPayload {
  uid: string;
  token: string;
  new_password: string;
  new_password_confirm: string;
}

export type AuthProvider = 'email' | 'google';

export interface UserProfile extends AuthUser {
  auth_provider: AuthProvider;
  updated_at: string;
}

export interface UserProfileUpdatePayload {
  full_name: string;
}

export type ThemePreference = 'light' | 'dark' | 'system';

export interface UserSettings {
  theme_preference: ThemePreference;
  email_notifications_enabled: boolean;
  updated_at: string;
}

export type UserSettingsUpdatePayload = Partial<
  Pick<UserSettings, 'theme_preference' | 'email_notifications_enabled'>
>;

export interface Session {
  id: number;
  created_at: string;
  expires_at: string;
}
