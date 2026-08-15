import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  createNoteCategoryRequest,
  deleteNoteCategoryRequest,
  listNoteCategoriesRequest,
  updateNoteCategoryRequest,
} from '@/features/notes/api';
import { NOTES_QUERY_KEY } from '@/features/notes/hooks/useNotes';
import type { CategoryPayload } from '@/features/notes/types';

export const NOTE_CATEGORIES_QUERY_KEY = [...NOTES_QUERY_KEY, 'categories'] as const;

function useInvalidateNotes() {
  const queryClient = useQueryClient();
  return () => queryClient.invalidateQueries({ queryKey: NOTES_QUERY_KEY });
}

export function useNoteCategories() {
  return useQuery({
    queryKey: NOTE_CATEGORIES_QUERY_KEY,
    queryFn: listNoteCategoriesRequest,
  });
}

export function useCreateNoteCategory() {
  const invalidateNotes = useInvalidateNotes();

  return useMutation({
    mutationFn: (payload: CategoryPayload) => createNoteCategoryRequest(payload),
    onSuccess: invalidateNotes,
  });
}

export function useUpdateNoteCategory() {
  const invalidateNotes = useInvalidateNotes();

  return useMutation({
    mutationFn: ({ categoryId, payload }: { categoryId: string; payload: CategoryPayload }) =>
      updateNoteCategoryRequest(categoryId, payload),
    onSuccess: invalidateNotes,
  });
}

export function useDeleteNoteCategory() {
  const invalidateNotes = useInvalidateNotes();

  return useMutation({
    mutationFn: (categoryId: string) => deleteNoteCategoryRequest(categoryId),
    onSuccess: invalidateNotes,
  });
}
