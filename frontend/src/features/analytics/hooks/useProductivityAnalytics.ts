import { useQuery } from '@tanstack/react-query';
import { getProductivityAnalyticsRequest } from '@/features/analytics/api';

export const PRODUCTIVITY_QUERY_KEY = ['analytics', 'productivity'] as const;

export function useProductivityAnalytics(days?: number) {
  return useQuery({
    queryKey: [...PRODUCTIVITY_QUERY_KEY, days ?? 'default'],
    queryFn: () => getProductivityAnalyticsRequest(days),
  });
}
