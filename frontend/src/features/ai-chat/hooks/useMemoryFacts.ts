import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  deleteMemoryFactRequest,
  listMemoryFactsRequest,
  updateMemoryFactRequest,
} from '@/features/ai-chat/api';
import type { MemoryFactFilters, MemoryFactPayload } from '@/features/ai-chat/types';

/**
 * ROADMAP.md Milestone 8 — Memory Engine: view/edit/delete controls over
 * the AI companion's stored long-term memory (PRD.md Section 13).
 */
export const MEMORY_FACTS_QUERY_KEY = ['ai-memory-facts'] as const;
export const memoryFactListQueryKey = (filters: MemoryFactFilters) =>
  [...MEMORY_FACTS_QUERY_KEY, 'list', filters] as const;

function useInvalidateMemoryFacts() {
  const queryClient = useQueryClient();
  return () => queryClient.invalidateQueries({ queryKey: MEMORY_FACTS_QUERY_KEY });
}

export function useMemoryFacts(filters: MemoryFactFilters = {}) {
  return useQuery({
    queryKey: memoryFactListQueryKey(filters),
    queryFn: () => listMemoryFactsRequest(filters),
  });
}

export function useUpdateMemoryFact() {
  const invalidateMemoryFacts = useInvalidateMemoryFacts();

  return useMutation({
    mutationFn: ({ factId, payload }: { factId: string; payload: MemoryFactPayload }) =>
      updateMemoryFactRequest(factId, payload),
    onSuccess: invalidateMemoryFacts,
  });
}

export function useDeleteMemoryFact() {
  const invalidateMemoryFacts = useInvalidateMemoryFacts();

  return useMutation({
    mutationFn: (factId: string) => deleteMemoryFactRequest(factId),
    onSuccess: invalidateMemoryFacts,
  });
}
