import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  createReminderRequest,
  deleteReminderRequest,
  listRemindersRequest,
  updateReminderRequest,
} from '@/features/reminders/api';
import type { ReminderFilters, ReminderPayload } from '@/features/reminders/types';

export const REMINDERS_QUERY_KEY = ['reminders'] as const;
export const reminderListQueryKey = (filters: ReminderFilters) =>
  [...REMINDERS_QUERY_KEY, 'list', filters] as const;

function useInvalidateReminders() {
  const queryClient = useQueryClient();
  return () => queryClient.invalidateQueries({ queryKey: REMINDERS_QUERY_KEY });
}

export function useReminders(filters: ReminderFilters = {}) {
  return useQuery({
    queryKey: reminderListQueryKey(filters),
    queryFn: () => listRemindersRequest(filters),
  });
}

export function useCreateReminder() {
  const invalidateReminders = useInvalidateReminders();

  return useMutation({
    mutationFn: (payload: ReminderPayload) => createReminderRequest(payload),
    onSuccess: invalidateReminders,
  });
}

export function useUpdateReminder() {
  const invalidateReminders = useInvalidateReminders();

  return useMutation({
    mutationFn: ({ reminderId, payload }: { reminderId: string; payload: ReminderPayload }) =>
      updateReminderRequest(reminderId, payload),
    onSuccess: invalidateReminders,
  });
}

export function useDeleteReminder() {
  const invalidateReminders = useInvalidateReminders();

  return useMutation({
    mutationFn: (reminderId: string) => deleteReminderRequest(reminderId),
    onSuccess: invalidateReminders,
  });
}
