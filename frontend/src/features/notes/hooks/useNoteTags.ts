import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { createNoteTagRequest, deleteNoteTagRequest, listNoteTagsRequest } from '@/features/notes/api';
import { NOTES_QUERY_KEY } from '@/features/notes/hooks/useNotes';
import type { TagPayload } from '@/features/notes/types';

export const NOTE_TAGS_QUERY_KEY = [...NOTES_QUERY_KEY, 'tags'] as const;

function useInvalidateNotes() {
  const queryClient = useQueryClient();
  return () => queryClient.invalidateQueries({ queryKey: NOTES_QUERY_KEY });
}

export function useNoteTags() {
  return useQuery({
    queryKey: NOTE_TAGS_QUERY_KEY,
    queryFn: listNoteTagsRequest,
  });
}

export function useCreateNoteTag() {
  const invalidateNotes = useInvalidateNotes();

  return useMutation({
    mutationFn: (payload: TagPayload) => createNoteTagRequest(payload),
    onSuccess: invalidateNotes,
  });
}

export function useDeleteNoteTag() {
  const invalidateNotes = useInvalidateNotes();

  return useMutation({
    mutationFn: (tagId: string) => deleteNoteTagRequest(tagId),
    onSuccess: invalidateNotes,
  });
}
