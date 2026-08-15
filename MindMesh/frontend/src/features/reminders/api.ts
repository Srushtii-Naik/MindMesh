import { apiClient } from '@/api/client';
import type { PaginatedResponse } from '@/types';
import type { Reminder, ReminderFilters, ReminderPayload } from '@/features/reminders/types';

/**
 * Reminders domain requests (ROADMAP.md Milestone 5 — foundational data
 * model and CRUD; delivery is deferred to Milestone 9). Consumed
 * exclusively via the TanStack Query hooks in `features/reminders/hooks/`,
 * per ARCHITECTURE.md Section 2.
 */

export async function listRemindersRequest(
  filters: ReminderFilters
): Promise<PaginatedResponse<Reminder>> {
  const { data } = await apiClient.get<PaginatedResponse<Reminder>>('/reminders/', {
    params: filters,
  });
  return data;
}

export async function createReminderRequest(payload: ReminderPayload): Promise<Reminder> {
  const { data } = await apiClient.post<Reminder>('/reminders/', payload);
  return data;
}

export async function updateReminderRequest(
  reminderId: string,
  payload: ReminderPayload
): Promise<Reminder> {
  const { data } = await apiClient.patch<Reminder>(`/reminders/${reminderId}/`, payload);
  return data;
}

export async function deleteReminderRequest(reminderId: string): Promise<void> {
  await apiClient.delete(`/reminders/${reminderId}/`);
}
