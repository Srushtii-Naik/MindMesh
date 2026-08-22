import { refreshAccessToken } from '@/api/client';
import { getProfileRequest } from '@/features/auth/api';
import { useAuthStore } from '@/features/auth/store';

/**
 * Attempts to restore a session on app start.
 *
 * Milestone 12 / ADR 0001: since the refresh token now lives only in an
 * httpOnly cookie (not localStorage), the store starts every page load
 * with `accessToken: null`. If the browser still holds a valid refresh
 * cookie from a prior visit, this silently exchanges it for a fresh access
 * token and loads the user's profile so they land back in the app instead
 * of being sent to /login. If there's no cookie (or it's expired/invalid),
 * this resolves quietly and the user is treated as signed out — never
 * throws, so callers don't need their own try/catch.
 */
export async function bootstrapSession(): Promise<void> {
  const { clearAuth, setBootstrapped } = useAuthStore.getState();

  try {
    await refreshAccessToken();
    const profile = await getProfileRequest();
    // Directly set state rather than `updateUser` (a merge-only action that
    // no-ops when `user` is still null, as it is on a fresh page load).
    useAuthStore.setState({
      user: {
        id: profile.id,
        email: profile.email,
        full_name: profile.full_name,
        created_at: profile.created_at,
      },
    });
  } catch {
    clearAuth();
  } finally {
    setBootstrapped();
  }
}
