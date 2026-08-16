import { useQuery } from '@tanstack/react-query';
import { listMemoryFactsRequest } from '@/features/ai-chat/api';

export const MEMORY_FACTS_QUERY_KEY = ['ai-memory-facts'] as const;

export function useMemoryFacts() {
  return useQuery({
    queryKey: MEMORY_FACTS_QUERY_KEY,
    queryFn: listMemoryFactsRequest,
  });
}
