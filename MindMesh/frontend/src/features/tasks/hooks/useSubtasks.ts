import { useMutation, useQueryClient } from '@tanstack/react-query';
import {
  createSubtaskRequest,
  deleteSubtaskRequest,
  updateSubtaskRequest,
} from '@/features/tasks/api';
import { TASKS_QUERY_KEY } from '@/features/tasks/hooks/useTasks';
import type { SubTaskPayload } from '@/features/tasks/types';

function useInvalidateTasks() {
  const queryClient = useQueryClient();
  return () => queryClient.invalidateQueries({ queryKey: TASKS_QUERY_KEY });
}

export function useCreateSubtask() {
  const invalidateTasks = useInvalidateTasks();

  return useMutation({
    mutationFn: ({ taskId, payload }: { taskId: string; payload: SubTaskPayload }) =>
      createSubtaskRequest(taskId, payload),
    onSuccess: invalidateTasks,
  });
}

export function useUpdateSubtask() {
  const invalidateTasks = useInvalidateTasks();

  return useMutation({
    mutationFn: ({
      taskId,
      subtaskId,
      payload,
    }: {
      taskId: string;
      subtaskId: string;
      payload: SubTaskPayload;
    }) => updateSubtaskRequest(taskId, subtaskId, payload),
    onSuccess: invalidateTasks,
  });
}

export function useDeleteSubtask() {
  const invalidateTasks = useInvalidateTasks();

  return useMutation({
    mutationFn: ({ taskId, subtaskId }: { taskId: string; subtaskId: string }) =>
      deleteSubtaskRequest(taskId, subtaskId),
    onSuccess: invalidateTasks,
  });
}
