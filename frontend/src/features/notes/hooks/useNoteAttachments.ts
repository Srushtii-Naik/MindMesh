import { useMutation, useQueryClient } from '@tanstack/react-query';
import {
  deleteNoteAttachmentRequest,
  downloadNoteAttachment,
  uploadNoteAttachmentRequest,
} from '@/features/notes/api';
import { NOTES_QUERY_KEY } from '@/features/notes/hooks/useNotes';

function useInvalidateNotes() {
  const queryClient = useQueryClient();
  return () => queryClient.invalidateQueries({ queryKey: NOTES_QUERY_KEY });
}

export function useUploadNoteAttachment() {
  const invalidateNotes = useInvalidateNotes();

  return useMutation({
    mutationFn: ({ noteId, file }: { noteId: string; file: File }) =>
      uploadNoteAttachmentRequest(noteId, file),
    onSuccess: invalidateNotes,
  });
}

export function useDeleteNoteAttachment() {
  const invalidateNotes = useInvalidateNotes();

  return useMutation({
    mutationFn: ({ noteId, attachmentId }: { noteId: string; attachmentId: string }) =>
      deleteNoteAttachmentRequest(noteId, attachmentId),
    onSuccess: invalidateNotes,
  });
}

export function useDownloadNoteAttachment() {
  return useMutation({
    mutationFn: ({
      noteId,
      attachmentId,
      filename,
    }: {
      noteId: string;
      attachmentId: string;
      filename: string;
    }) => downloadNoteAttachment(noteId, attachmentId, filename),
  });
}
