import { describe, it, expect, beforeEach } from 'vitest';
import { useAuthStore } from '@/features/auth/store';

const user = {
  id: 'user-1',
  email: 'jane@example.com',
  full_name: 'Jane Doe',
  created_at: '2026-01-01T00:00:00Z',
};

const tokens = { access: 'access-token' };

describe('useAuthStore', () => {
  beforeEach(() => {
    useAuthStore.getState().clearAuth();
  });

  it('starts unauthenticated', () => {
    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(false);
    expect(state.user).toBeNull();
    expect(state.accessToken).toBeNull();
  });

  it('setAuth stores the user and access token, and marks authenticated', () => {
    useAuthStore.getState().setAuth(user, tokens);
    const state = useAuthStore.getState();

    expect(state.isAuthenticated).toBe(true);
    expect(state.user).toEqual(user);
    expect(state.accessToken).toBe('access-token');
  });

  it('setAccessToken updates only the token, leaving the user untouched', () => {
    useAuthStore.getState().setAuth(user, tokens);
    useAuthStore.getState().setAccessToken('new-access');

    const state = useAuthStore.getState();
    expect(state.user).toEqual(user);
    expect(state.accessToken).toBe('new-access');
    expect(state.isAuthenticated).toBe(true);
  });

  it('updateUser merges a partial patch into the existing user', () => {
    useAuthStore.getState().setAuth(user, tokens);
    useAuthStore.getState().updateUser({ full_name: 'Jane Updated' });

    expect(useAuthStore.getState().user).toEqual({ ...user, full_name: 'Jane Updated' });
  });

  it('updateUser is a no-op when there is no user', () => {
    useAuthStore.getState().updateUser({ full_name: 'Ghost' });
    expect(useAuthStore.getState().user).toBeNull();
  });

  it('clearAuth resets everything', () => {
    useAuthStore.getState().setAuth(user, tokens);
    useAuthStore.getState().clearAuth();

    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(false);
    expect(state.user).toBeNull();
    expect(state.accessToken).toBeNull();
  });

  it('setBootstrapped marks the initial session-restore attempt as complete', () => {
    expect(useAuthStore.getState().hasBootstrapped).toBe(false);
    useAuthStore.getState().setBootstrapped();
    expect(useAuthStore.getState().hasBootstrapped).toBe(true);
  });
});
