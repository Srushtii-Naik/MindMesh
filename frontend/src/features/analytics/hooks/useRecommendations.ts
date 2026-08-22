import { useQuery } from '@tanstack/react-query';
import { getRecommendationsRequest } from '@/features/analytics/api';

export const RECOMMENDATIONS_QUERY_KEY = ['analytics', 'recommendations'] as const;

export function useRecommendations() {
  return useQuery({
    queryKey: RECOMMENDATIONS_QUERY_KEY,
    queryFn: getRecommendationsRequest,
  });
}
