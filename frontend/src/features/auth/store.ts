import { create } from 'zustand';
import type { AuthTokens, AuthUser } from '@/features/auth/types';

/**
 * Auth session state.
 *
 * Milestone 12 / ADR 0001 (docs/adr/0001-token-storage-strategy.md): the
 * refresh token is no longer stored here — it lives exclusively in an
 * httpOnly cookie the browser manages, unreachable by JavaScript (and
 * therefore by XSS). This store now only holds the short-lived access
 * token (in memory only) and the current user, and is NOT persisted to
 * localStorage — persisting `isAuthenticated`/`user` without a way to
 * verify them against the server would let a stale, no-longer-valid
 * "logged in" state survive a session that was actually revoked
 * server-side. Session continuity across a page reload is instead
 * restored by `features/auth/bootstrap.ts`, which calls the refresh
 * endpoint (using the httpOnly cookie) on app start.
 *
 * Exposed as a vanilla store (not just a hook) so the Axios client — which
 * lives outside the React tree — can read and update the access token
 * directly via `useAuthStore.getState()` / `.setState()`.
 */
interface AuthState {
  user: AuthUser | null;
  accessToken: string | null;
  isAuthenticated: boolean;
  /** True once the initial session-restore attempt (bootstrap.ts) has finished. */
  hasBootstrapped: boolean;
  setAuth: (user: AuthUser, tokens: AuthTokens) => void;
  setAccessToken: (accessToken: string) => void;
  updateUser: (patch: Partial<AuthUser>) => void;
  clearAuth: () => void;
  setBootstrapped: () => void;
}

export const useAuthStore = create<AuthState>()((set) => ({
  user: null,
  accessToken: null,
  isAuthenticated: false,
  hasBootstrapped: false,

  setAuth: (user, tokens) =>
    set({
      user,
      accessToken: tokens.access,
      isAuthenticated: true,
    }),

  setAccessToken: (accessToken) =>
    set({
      accessToken,
      isAuthenticated: true,
    }),

  updateUser: (patch) =>
    set((state) => ({
      user: state.user ? { ...state.user, ...patch } : state.user,
    })),

  clearAuth: () =>
    set({
      user: null,
      accessToken: null,
      isAuthenticated: false,
    }),

  setBootstrapped: () => set({ hasBootstrapped: true }),
}));
