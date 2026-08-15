import { useQuery } from '@tanstack/react-query';
import {
  getCalendarViewRequest,
  getDailyPlannerRequest,
  getWeeklyPlannerRequest,
} from '@/features/calendar/api';
import { CALENDAR_QUERY_KEY } from '@/features/calendar/hooks/useEvents';
import type { IsoDate } from '@/features/calendar/types';

/** Powers the month grid (ROADMAP.md Milestone 5: "Calendar views render correctly"). */
export function useCalendarView(start: IsoDate, end: IsoDate) {
  return useQuery({
    queryKey: [...CALENDAR_QUERY_KEY, 'view', start, end] as const,
    queryFn: () => getCalendarViewRequest(start, end),
  });
}

/** Powers the daily planner (ROADMAP.md Milestone 5: "Daily and weekly planners functional"). */
export function useDailyPlanner(date: IsoDate) {
  return useQuery({
    queryKey: [...CALENDAR_QUERY_KEY, 'daily', date] as const,
    queryFn: () => getDailyPlannerRequest(date),
  });
}

/** Powers the weekly planner (ROADMAP.md Milestone 5: "Daily and weekly planners functional"). */
export function useWeeklyPlanner(weekStart: IsoDate) {
  return useQuery({
    queryKey: [...CALENDAR_QUERY_KEY, 'weekly', weekStart] as const,
    queryFn: () => getWeeklyPlannerRequest(weekStart),
  });
}
