import type { Task } from '@/features/tasks/types';

export interface LinkedTask {
  id: string;
  title: string;
  is_completed: boolean;
}

export interface CalendarEvent {
  id: string;
  title: string;
  description: string;
  location: string;
  start_time: string;
  end_time: string;
  all_day: boolean;
  color: string;
  task: LinkedTask | null;
  created_at: string;
  updated_at: string;
}

export interface EventPayload {
  title?: string;
  description?: string;
  location?: string;
  start_time?: string;
  end_time?: string;
  all_day?: boolean;
  color?: string;
  task_id?: string | null;
}

export interface EventFilters {
  start?: string;
  end?: string;
  task_id?: string;
  search?: string;
}

/** ISO date string (YYYY-MM-DD), not a full timestamp — matches the backend's DateField query params. */
export type IsoDate = string;

export interface CalendarView {
  events: CalendarEvent[];
  tasks: Task[];
}

export interface DailyPlanner {
  date: IsoDate;
  events: CalendarEvent[];
  tasks: Task[];
}

export interface WeeklyPlannerDay {
  date: IsoDate;
  events: CalendarEvent[];
  tasks: Task[];
}

export interface WeeklyPlanner {
  week_start: IsoDate;
  week_end: IsoDate;
  days: WeeklyPlannerDay[];
}

export type CalendarViewMode = 'month' | 'week' | 'day';
