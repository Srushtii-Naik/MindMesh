import { apiClient } from '@/api/client';
import type {
  AuthResponse,
  GoogleAuthPayload,
  LoginPayload,
  PasswordResetConfirmPayload,
  PasswordResetRequestPayload,
  RegisterPayload,
  Session,
  UserProfile,
  UserProfileUpdatePayload,
  UserSettings,
  UserSettingsUpdatePayload,
} from '@/features/auth/types';

/**
 * Auth domain requests. Consumed exclusively via the TanStack Query hooks in
 * `features/auth/hooks/` — no component calls these directly, per
 * ARCHITECTURE.md Section 2 ("No direct fetch calls inside components").
 */

export async function loginRequest(payload: LoginPayload): Promise<AuthResponse> {
  const { data } = await apiClient.post<AuthResponse>('/auth/login/', payload);
  return data;
}

export async function registerRequest(payload: RegisterPayload): Promise<AuthResponse> {
  const { data } = await apiClient.post<AuthResponse>('/auth/register/', payload);
  return data;
}

export async function logoutRequest(refresh: string): Promise<void> {
  await apiClient.post('/auth/logout/', { refresh });
}

export async function googleLoginRequest(payload: GoogleAuthPayload): Promise<AuthResponse> {
  const { data } = await apiClient.post<AuthResponse>('/auth/google/', payload);
  return data;
}

export async function requestPasswordResetRequest(
  payload: PasswordResetRequestPayload
): Promise<{ detail: string }> {
  const { data } = await apiClient.post<{ detail: string }>('/auth/password-reset/', payload);
  return data;
}

export async function confirmPasswordResetRequest(
  payload: PasswordResetConfirmPayload
): Promise<{ detail: string }> {
  const { data } = await apiClient.post<{ detail: string }>(
    '/auth/password-reset/confirm/',
    payload
  );
  return data;
}

export async function getProfileRequest(): Promise<UserProfile> {
  const { data } = await apiClient.get<UserProfile>('/auth/me/');
  return data;
}

export async function updateProfileRequest(
  payload: UserProfileUpdatePayload
): Promise<UserProfile> {
  const { data } = await apiClient.patch<UserProfile>('/auth/me/', payload);
  return data;
}

export async function getSettingsRequest(): Promise<UserSettings> {
  const { data } = await apiClient.get<UserSettings>('/auth/settings/');
  return data;
}

export async function updateSettingsRequest(
  payload: UserSettingsUpdatePayload
): Promise<UserSettings> {
  const { data } = await apiClient.patch<UserSettings>('/auth/settings/', payload);
  return data;
}

export async function listSessionsRequest(): Promise<Session[]> {
  const { data } = await apiClient.get<Session[]>('/auth/sessions/');
  return data;
}

export async function revokeSessionRequest(sessionId: number): Promise<void> {
  await apiClient.post(`/auth/sessions/${sessionId}/revoke/`);
}

export async function revokeAllSessionsRequest(): Promise<void> {
  await apiClient.post('/auth/sessions/revoke-all/');
}
