/** Shapes returned by /api/v1/analytics/* (ROADMAP.md Milestone 11). */

export interface DailySeriesPoint {
  date: string;
  tasks_completed: number;
  tasks_created: number;
}

export interface ProductivityAnalytics {
  period_start: string;
  period_end: string;
  tasks_created: number;
  tasks_completed: number;
  completion_rate: number;
  notes_created: number;
  events_scheduled: number;
  daily_series: DailySeriesPoint[];
}

export interface DailyActivityPoint {
  date: string;
  is_active_day: boolean;
}

export interface HabitTracking {
  period_start: string;
  period_end: string;
  current_streak_days: number;
  longest_streak_days: number;
  daily_activity: DailyActivityPoint[];
}

export interface Recommendations {
  recommendations: string[];
}

export interface ProgressReport {
  id: string;
  period_start: string;
  period_end: string;
  tasks_created: number;
  tasks_completed: number;
  completion_rate: number;
  notes_created: number;
  events_scheduled: number;
  current_streak_days: number;
  longest_streak_days: number;
  ai_summary: string;
  created_at: string;
}
