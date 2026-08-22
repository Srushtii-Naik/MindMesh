/**
 * Dashboard feature types.
 *
 * The dashboard has no domain data of its own (ARCHITECTURE.md Section 9 —
 * there is no backend `dashboard` app; it is a composition surface over
 * other domains). At this stage the only domain with real data is
 * `accounts`, so `ActivityItem` is derived entirely from existing
 * profile/settings/session data — see `utils.ts`.
 */

export type ActivityKind = 'account_created' | 'profile_updated' | 'settings_updated' | 'session';

export interface ActivityItem {
  id: string;
  kind: ActivityKind;
  label: string;
  timestamp: string;
}
