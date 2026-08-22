import { useQuery } from '@tanstack/react-query';
import { getHabitTrackingRequest } from '@/features/analytics/api';

export const HABIT_TRACKING_QUERY_KEY = ['analytics', 'habits'] as const;

export function useHabitTracking(days?: number) {
  return useQuery({
    queryKey: [...HABIT_TRACKING_QUERY_KEY, days ?? 'default'],
    queryFn: () => getHabitTrackingRequest(days),
  });
}
