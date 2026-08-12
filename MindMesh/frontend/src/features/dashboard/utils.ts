import type { Session, UserProfile, UserSettings } from '@/features/auth/types';
import type { ActivityItem } from '@/features/dashboard/types';

/**
 * A settings row is created automatically at registration (see backend
 * apps/accounts/services.py `get_or_create_settings`), so its `updated_at`
 * is initially just the moment the account was created — not a genuine
 * preference change. This threshold distinguishes "the user actually
 * changed a setting" from "the default row was created alongside the
 * account", so the activity feed only reports real actions.
 */
const SETTINGS_CHANGE_THRESHOLD_MS = 60_000;

/**
 * Builds the recent-activity feed shown on the dashboard, sourced entirely
 * from data that already exists in the `accounts` domain (there is no
 * dedicated activity/audit model — see ROADMAP.md Milestone 3, which has no
 * backend deliverable, and PROJECT_RULES.md Section 1 on not building ahead
 * of a defined need). Every item here corresponds to something the user
 * actually did: creating their account, editing their profile, changing a
 * preference, or signing in on a device.
 */
export function buildActivityFeed(
  profile: UserProfile | undefined,
  settings: UserSettings | undefined,
  sessions: Session[] | undefined
): ActivityItem[] {
  const items: ActivityItem[] = [];

  if (profile) {
    items.push({
      id: 'account-created',
      kind: 'account_created',
      label: 'Account created',
      timestamp: profile.created_at,
    });

    if (profile.updated_at !== profile.created_at) {
      items.push({
        id: 'profile-updated',
        kind: 'profile_updated',
        label: 'Profile updated',
        timestamp: profile.updated_at,
      });
    }

    if (
      settings &&
      Math.abs(new Date(settings.updated_at).getTime() - new Date(profile.created_at).getTime()) >
        SETTINGS_CHANGE_THRESHOLD_MS
    ) {
      items.push({
        id: 'settings-updated',
        kind: 'settings_updated',
        label: 'Preferences updated',
        timestamp: settings.updated_at,
      });
    }
  }

  for (const session of sessions ?? []) {
    items.push({
      id: `session-${session.id}`,
      kind: 'session',
      label: 'Signed in',
      timestamp: session.created_at,
    });
  }

  return items.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
}
