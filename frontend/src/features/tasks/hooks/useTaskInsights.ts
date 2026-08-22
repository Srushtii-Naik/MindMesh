import { useQuery } from '@tanstack/react-query';
import { getTaskSuggestionsRequest, getTodaySummaryRequest } from '@/features/tasks/api';
import { TASKS_QUERY_KEY } from '@/features/tasks/hooks/useTasks';

export const SUGGESTIONS_QUERY_KEY = [...TASKS_QUERY_KEY, 'suggestions'] as const;
export const TODAY_SUMMARY_QUERY_KEY = [...TASKS_QUERY_KEY, 'summary', 'today'] as const;

/** Rule-based smart suggestions (ROADMAP.md Milestone 4). */
export function useTaskSuggestions() {
  return useQuery({
    queryKey: SUGGESTIONS_QUERY_KEY,
    queryFn: getTaskSuggestionsRequest,
  });
}

/** Powers the dashboard's Today's Summary card. */
export function useTodaySummary() {
  return useQuery({
    queryKey: TODAY_SUMMARY_QUERY_KEY,
    queryFn: getTodaySummaryRequest,
  });
}
