export type Priority = 'low' | 'medium' | 'high' | 'urgent';

export type RecurrenceRule = 'none' | 'daily' | 'weekly' | 'monthly';

export interface Category {
  id: string;
  name: string;
  color: string;
  created_at: string;
  updated_at: string;
}

export interface CategoryPayload {
  name: string;
  color?: string;
}

export interface SubTask {
  id: string;
  title: string;
  is_completed: boolean;
  order: number;
  created_at: string;
  updated_at: string;
}

export interface SubTaskPayload {
  title?: string;
  is_completed?: boolean;
  order?: number;
}

export interface Task {
  id: string;
  title: string;
  description: string;
  category: Category | null;
  priority: Priority;
  due_date: string | null;
  is_completed: boolean;
  completed_at: string | null;
  recurrence: RecurrenceRule;
  recurrence_interval: number;
  subtasks: SubTask[];
  created_at: string;
  updated_at: string;
}

export interface TaskPayload {
  title?: string;
  description?: string;
  category_id?: string | null;
  priority?: Priority;
  due_date?: string | null;
  recurrence?: RecurrenceRule;
  recurrence_interval?: number;
}

export interface TaskFilters {
  priority?: Priority;
  category_id?: string;
  is_completed?: boolean;
  due_before?: string;
  due_after?: string;
  search?: string;
}

export type SuggestionKind = 'overdue' | 'due_today' | 'missing_due_date' | 'ready_to_complete';

export interface TaskSuggestion {
  id: string;
  kind: SuggestionKind;
  message: string;
  task_id: string | null;
}

export interface TodaySummary {
  due_today_count: number;
  overdue_count: number;
  completed_today_count: number;
}
