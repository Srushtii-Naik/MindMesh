import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  createEventRequest,
  deleteEventRequest,
  getEventRequest,
  listEventsRequest,
  updateEventRequest,
} from '@/features/calendar/api';
import type { EventFilters, EventPayload } from '@/features/calendar/types';

export const CALENDAR_QUERY_KEY = ['calendar'] as const;
export const eventListQueryKey = (filters: EventFilters) =>
  [...CALENDAR_QUERY_KEY, 'events', filters] as const;
export const eventDetailQueryKey = (eventId: string) =>
  [...CALENDAR_QUERY_KEY, 'event', eventId] as const;

/**
 * Every mutation below invalidates the whole `['calendar']` prefix, the
 * same broad-invalidation pattern `features/tasks` uses — an event change
 * can affect the event list, the combined view, and both planners at once.
 */
function useInvalidateCalendar() {
  const queryClient = useQueryClient();
  return () => queryClient.invalidateQueries({ queryKey: CALENDAR_QUERY_KEY });
}

export function useEvents(filters: EventFilters = {}) {
  return useQuery({
    queryKey: eventListQueryKey(filters),
    queryFn: () => listEventsRequest(filters),
  });
}

export function useEvent(eventId: string | undefined) {
  return useQuery({
    queryKey: eventDetailQueryKey(eventId ?? ''),
    queryFn: () => getEventRequest(eventId as string),
    enabled: Boolean(eventId),
  });
}

export function useCreateEvent() {
  const invalidateCalendar = useInvalidateCalendar();

  return useMutation({
    mutationFn: (payload: EventPayload) => createEventRequest(payload),
    onSuccess: invalidateCalendar,
  });
}

export function useUpdateEvent() {
  const invalidateCalendar = useInvalidateCalendar();

  return useMutation({
    mutationFn: ({ eventId, payload }: { eventId: string; payload: EventPayload }) =>
      updateEventRequest(eventId, payload),
    onSuccess: invalidateCalendar,
  });
}

export function useDeleteEvent() {
  const invalidateCalendar = useInvalidateCalendar();

  return useMutation({
    mutationFn: (eventId: string) => deleteEventRequest(eventId),
    onSuccess: invalidateCalendar,
  });
}
