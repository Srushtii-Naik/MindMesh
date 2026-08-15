import { apiClient } from '@/api/client';
import type { PaginatedResponse } from '@/types';
import type {
  CalendarEvent,
  CalendarView,
  DailyPlanner,
  EventFilters,
  EventPayload,
  IsoDate,
  WeeklyPlanner,
} from '@/features/calendar/types';

/**
 * Calendar & Scheduling domain requests (ROADMAP.md Milestone 5). Consumed
 * exclusively via the TanStack Query hooks in `features/calendar/hooks/` —
 * no component calls these directly, per ARCHITECTURE.md Section 2.
 */

export async function listEventsRequest(
  filters: EventFilters
): Promise<PaginatedResponse<CalendarEvent>> {
  const { data } = await apiClient.get<PaginatedResponse<CalendarEvent>>('/calendar/events/', {
    params: filters,
  });
  return data;
}

export async function getEventRequest(eventId: string): Promise<CalendarEvent> {
  const { data } = await apiClient.get<CalendarEvent>(`/calendar/events/${eventId}/`);
  return data;
}

export async function createEventRequest(payload: EventPayload): Promise<CalendarEvent> {
  const { data } = await apiClient.post<CalendarEvent>('/calendar/events/', payload);
  return data;
}

export async function updateEventRequest(
  eventId: string,
  payload: EventPayload
): Promise<CalendarEvent> {
  const { data } = await apiClient.patch<CalendarEvent>(`/calendar/events/${eventId}/`, payload);
  return data;
}

export async function deleteEventRequest(eventId: string): Promise<void> {
  await apiClient.delete(`/calendar/events/${eventId}/`);
}

export async function getCalendarViewRequest(start: IsoDate, end: IsoDate): Promise<CalendarView> {
  const { data } = await apiClient.get<CalendarView>('/calendar/view/', { params: { start, end } });
  return data;
}

export async function getDailyPlannerRequest(date: IsoDate): Promise<DailyPlanner> {
  const { data } = await apiClient.get<DailyPlanner>('/calendar/planner/daily/', {
    params: { date },
  });
  return data;
}

export async function getWeeklyPlannerRequest(start: IsoDate): Promise<WeeklyPlanner> {
  const { data } = await apiClient.get<WeeklyPlanner>('/calendar/planner/weekly/', {
    params: { start },
  });
  return data;
}
