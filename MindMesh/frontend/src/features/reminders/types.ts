export type ReminderTriggerType = 'time';

export interface LinkedRef {
  id: string;
  title: string;
}

export interface Reminder {
  id: string;
  title: string;
  message: string;
  trigger_type: ReminderTriggerType;
  remind_at: string;
  task: LinkedRef | null;
  event: LinkedRef | null;
  is_sent: boolean;
  sent_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface ReminderPayload {
  title?: string;
  message?: string;
  remind_at?: string;
  task_id?: string | null;
  event_id?: string | null;
}

export interface ReminderFilters {
  is_sent?: boolean;
  before?: string;
  after?: string;
  task_id?: string;
  event_id?: string;
}
