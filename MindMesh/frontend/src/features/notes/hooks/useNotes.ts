import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  createNoteRequest,
  deleteNoteRequest,
  generateNoteSummaryRequest,
  getNoteRequest,
  listNotesRequest,
  updateNoteRequest,
} from '@/features/notes/api';
import type { NoteFilters, NotePayload } from '@/features/notes/types';

export const NOTES_QUERY_KEY = ['notes'] as const;
export const noteListQueryKey = (filters: NoteFilters) =>
  [...NOTES_QUERY_KEY, 'list', filters] as const;
export const noteDetailQueryKey = (noteId: string) => [...NOTES_QUERY_KEY, 'detail', noteId] as const;

/**
 * Every mutation below invalidates the whole `['notes']` prefix rather than
 * a narrower key — mirrors features/tasks/hooks/useTasks.ts's reasoning: a
 * note change can affect its own list entry and any filtered view of it,
 * so a broad invalidation is simpler and safer than tracking each dependency.
 */
function useInvalidateNotes() {
  const queryClient = useQueryClient();
  return () => queryClient.invalidateQueries({ queryKey: NOTES_QUERY_KEY });
}

export function useNotes(filters: NoteFilters = {}) {
  return useQuery({
    queryKey: noteListQueryKey(filters),
    queryFn: () => listNotesRequest(filters),
  });
}

export function useNote(noteId: string | undefined) {
  return useQuery({
    queryKey: noteDetailQueryKey(noteId ?? ''),
    queryFn: () => getNoteRequest(noteId as string),
    enabled: Boolean(noteId),
  });
}

export function useCreateNote() {
  const invalidateNotes = useInvalidateNotes();

  return useMutation({
    mutationFn: (payload: NotePayload) => createNoteRequest(payload),
    onSuccess: invalidateNotes,
  });
}

export function useUpdateNote() {
  const invalidateNotes = useInvalidateNotes();

  return useMutation({
    mutationFn: ({ noteId, payload }: { noteId: string; payload: NotePayload }) =>
      updateNoteRequest(noteId, payload),
    onSuccess: invalidateNotes,
  });
}

export function useDeleteNote() {
  const invalidateNotes = useInvalidateNotes();

  return useMutation({
    mutationFn: (noteId: string) => deleteNoteRequest(noteId),
    onSuccess: invalidateNotes,
  });
}

export function useGenerateNoteSummary() {
  const invalidateNotes = useInvalidateNotes();

  return useMutation({
    mutationFn: (noteId: string) => generateNoteSummaryRequest(noteId),
    onSuccess: invalidateNotes,
  });
}
