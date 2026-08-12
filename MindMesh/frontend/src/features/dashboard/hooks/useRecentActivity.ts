import { useProfile, useSessions, useSettings } from '@/features/auth';
import { buildActivityFeed } from '@/features/dashboard/utils';

/**
 * Derives the dashboard's recent-activity feed from data the app already
 * fetches elsewhere (profile, settings, sessions) rather than introducing a
 * new endpoint or domain — see utils.ts for the rationale.
 */
export function useRecentActivity() {
  const profile = useProfile();
  const settings = useSettings();
  const sessions = useSessions();

  const isLoading = profile.isLoading || settings.isLoading || sessions.isLoading;
  const isError = profile.isError || settings.isError || sessions.isError;

  return {
    items: buildActivityFeed(profile.data, settings.data, sessions.data),
    isLoading,
    isError,
  };
}
