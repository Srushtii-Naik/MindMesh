import { useQuery } from '@tanstack/react-query';
import { getAISuggestionsRequest } from '@/features/ai-chat/api';

export const AI_SUGGESTIONS_QUERY_KEY = ['ai-suggestions'] as const;

export function useAISuggestions() {
  return useQuery({
    queryKey: AI_SUGGESTIONS_QUERY_KEY,
    queryFn: getAISuggestionsRequest,
  });
}
