import { describe, it, expect } from 'vitest';
import { buildActivityFeed } from '@/features/dashboard/utils';
import type { Session, UserProfile, UserSettings } from '@/features/auth/types';

const baseProfile: UserProfile = {
  id: 'user-1',
  email: 'jane@example.com',
  full_name: 'Jane Doe',
  created_at: '2026-01-01T09:00:00Z',
  auth_provider: 'email',
  updated_at: '2026-01-01T09:00:00Z',
};

describe('buildActivityFeed', () => {
  it('returns an empty list when there is no data yet', () => {
    expect(buildActivityFeed(undefined, undefined, undefined)).toEqual([]);
  });

  it('includes only "Account created" when nothing else has changed', () => {
    const items = buildActivityFeed(baseProfile, undefined, undefined);

    expect(items).toEqual([
      {
        id: 'account-created',
        kind: 'account_created',
        label: 'Account created',
        timestamp: baseProfile.created_at,
      },
    ]);
  });

  it('adds a "Profile updated" item when updated_at differs from created_at', () => {
    const profile: UserProfile = { ...baseProfile, updated_at: '2026-02-01T09:00:00Z' };
    const items = buildActivityFeed(profile, undefined, undefined);

    expect(items.map((item) => item.kind)).toEqual(['profile_updated', 'account_created']);
  });

  it('ignores the settings row auto-created alongside the account', () => {
    const settings: UserSettings = {
      theme_preference: 'system',
      email_notifications_enabled: true,
      updated_at: '2026-01-01T09:00:05Z', // 5s after account creation — not a real change
    };

    const items = buildActivityFeed(baseProfile, settings, undefined);

    expect(items.some((item) => item.kind === 'settings_updated')).toBe(false);
  });

  it('includes "Preferences updated" when settings changed well after account creation', () => {
    const settings: UserSettings = {
      theme_preference: 'dark',
      email_notifications_enabled: false,
      updated_at: '2026-03-01T09:00:00Z',
    };

    const items = buildActivityFeed(baseProfile, settings, undefined);

    expect(items.some((item) => item.kind === 'settings_updated')).toBe(true);
  });

  it('includes one "Signed in" item per session', () => {
    const sessions: Session[] = [
      { id: 1, created_at: '2026-01-02T08:00:00Z', expires_at: '2026-01-09T08:00:00Z' },
      { id: 2, created_at: '2026-01-03T08:00:00Z', expires_at: '2026-01-10T08:00:00Z' },
    ];

    const items = buildActivityFeed(baseProfile, undefined, sessions);

    expect(items.filter((item) => item.kind === 'session')).toHaveLength(2);
    expect(items.map((item) => item.id)).toContain('session-1');
    expect(items.map((item) => item.id)).toContain('session-2');
  });

  it('sorts every item newest first', () => {
    const profile: UserProfile = { ...baseProfile, updated_at: '2026-01-05T09:00:00Z' };
    const sessions: Session[] = [
      { id: 1, created_at: '2026-01-10T08:00:00Z', expires_at: '2026-01-17T08:00:00Z' },
    ];

    const items = buildActivityFeed(profile, undefined, sessions);
    const timestamps = items.map((item) => new Date(item.timestamp).getTime());

    expect(timestamps).toEqual([...timestamps].sort((a, b) => b - a));
  });
});
