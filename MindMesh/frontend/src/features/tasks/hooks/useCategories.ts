import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  createCategoryRequest,
  deleteCategoryRequest,
  listCategoriesRequest,
  updateCategoryRequest,
} from '@/features/tasks/api';
import { TASKS_QUERY_KEY } from '@/features/tasks/hooks/useTasks';
import type { CategoryPayload } from '@/features/tasks/types';

export const CATEGORIES_QUERY_KEY = [...TASKS_QUERY_KEY, 'categories'] as const;

function useInvalidateTasks() {
  const queryClient = useQueryClient();
  return () => queryClient.invalidateQueries({ queryKey: TASKS_QUERY_KEY });
}

export function useCategories() {
  return useQuery({
    queryKey: CATEGORIES_QUERY_KEY,
    queryFn: listCategoriesRequest,
  });
}

export function useCreateCategory() {
  const invalidateTasks = useInvalidateTasks();

  return useMutation({
    mutationFn: (payload: CategoryPayload) => createCategoryRequest(payload),
    onSuccess: invalidateTasks,
  });
}

export function useUpdateCategory() {
  const invalidateTasks = useInvalidateTasks();

  return useMutation({
    mutationFn: ({ categoryId, payload }: { categoryId: string; payload: CategoryPayload }) =>
      updateCategoryRequest(categoryId, payload),
    onSuccess: invalidateTasks,
  });
}

export function useDeleteCategory() {
  const invalidateTasks = useInvalidateTasks();

  return useMutation({
    mutationFn: (categoryId: string) => deleteCategoryRequest(categoryId),
    onSuccess: invalidateTasks,
  });
}
