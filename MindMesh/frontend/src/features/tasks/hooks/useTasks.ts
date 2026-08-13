import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  completeTaskRequest,
  createTaskRequest,
  deleteTaskRequest,
  getTaskRequest,
  listTasksRequest,
  reopenTaskRequest,
  updateTaskRequest,
} from '@/features/tasks/api';
import type { TaskFilters, TaskPayload } from '@/features/tasks/types';

export const TASKS_QUERY_KEY = ['tasks'] as const;
export const taskListQueryKey = (filters: TaskFilters) =>
  [...TASKS_QUERY_KEY, 'list', filters] as const;
export const taskDetailQueryKey = (taskId: string) =>
  [...TASKS_QUERY_KEY, 'detail', taskId] as const;

/**
 * Every mutation below invalidates the whole `['tasks']` prefix rather than
 * a narrower key. A task change can affect its own list entry, the
 * suggestions list, and the dashboard's today-summary all at once, so a
 * broad invalidation is simpler and safer than tracking each dependency.
 */
function useInvalidateTasks() {
  const queryClient = useQueryClient();
  return () => queryClient.invalidateQueries({ queryKey: TASKS_QUERY_KEY });
}

export function useTasks(filters: TaskFilters = {}) {
  return useQuery({
    queryKey: taskListQueryKey(filters),
    queryFn: () => listTasksRequest(filters),
  });
}

export function useTask(taskId: string | undefined) {
  return useQuery({
    queryKey: taskDetailQueryKey(taskId ?? ''),
    queryFn: () => getTaskRequest(taskId as string),
    enabled: Boolean(taskId),
  });
}

export function useCreateTask() {
  const invalidateTasks = useInvalidateTasks();

  return useMutation({
    mutationFn: (payload: TaskPayload) => createTaskRequest(payload),
    onSuccess: invalidateTasks,
  });
}

export function useUpdateTask() {
  const invalidateTasks = useInvalidateTasks();

  return useMutation({
    mutationFn: ({ taskId, payload }: { taskId: string; payload: TaskPayload }) =>
      updateTaskRequest(taskId, payload),
    onSuccess: invalidateTasks,
  });
}

export function useDeleteTask() {
  const invalidateTasks = useInvalidateTasks();

  return useMutation({
    mutationFn: (taskId: string) => deleteTaskRequest(taskId),
    onSuccess: invalidateTasks,
  });
}

export function useCompleteTask() {
  const invalidateTasks = useInvalidateTasks();

  return useMutation({
    mutationFn: (taskId: string) => completeTaskRequest(taskId),
    onSuccess: invalidateTasks,
  });
}

export function useReopenTask() {
  const invalidateTasks = useInvalidateTasks();

  return useMutation({
    mutationFn: (taskId: string) => reopenTaskRequest(taskId),
    onSuccess: invalidateTasks,
  });
}
