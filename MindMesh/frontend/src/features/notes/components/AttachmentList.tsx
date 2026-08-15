import { useRef } from 'react';
import { extractApiErrorMessage } from '@/api/errors';
import {
  useDeleteNoteAttachment,
  useDownloadNoteAttachment,
  useUploadNoteAttachment,
} from '@/features/notes/hooks';
import type { NoteAttachment } from '@/features/notes/types';

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

interface AttachmentListProps {
  noteId: string;
  attachments: NoteAttachment[];
}

/** File attachments for a note (ROADMAP.md Milestone 6: "Attachments"). */
export function AttachmentList({ noteId, attachments }: AttachmentListProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const uploadAttachment = useUploadNoteAttachment();
  const deleteAttachment = useDeleteNoteAttachment();
  const downloadAttachment = useDownloadNoteAttachment();

  const handleFileSelected = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    uploadAttachment.mutate({ noteId, file });
    event.target.value = '';
  };

  return (
    <div className="space-y-2">
      <h3 className="text-sm font-medium text-slate-700 dark:text-slate-300">Attachments</h3>

      {attachments.length > 0 && (
        <ul className="space-y-1.5">
          {attachments.map((attachment) => (
            <li
              key={attachment.id}
              className="flex items-center justify-between gap-2 rounded-md border border-slate-200 px-2.5 py-1.5 text-sm dark:border-slate-700"
            >
              <button
                type="button"
                onClick={() =>
                  downloadAttachment.mutate({
                    noteId,
                    attachmentId: attachment.id,
                    filename: attachment.original_filename,
                  })
                }
                className="min-w-0 truncate text-left text-brand-600 hover:underline dark:text-brand-400"
              >
                {attachment.original_filename}
              </button>
              <div className="flex shrink-0 items-center gap-2">
                <span className="text-xs text-slate-400">{formatSize(attachment.size_bytes)}</span>
                <button
                  type="button"
                  onClick={() => deleteAttachment.mutate({ noteId, attachmentId: attachment.id })}
                  aria-label={`Delete ${attachment.original_filename}`}
                  className="text-xs font-medium text-slate-500 hover:text-red-600 dark:text-slate-400 dark:hover:text-red-400"
                >
                  Delete
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}

      <div>
        <input
          ref={fileInputRef}
          type="file"
          onChange={handleFileSelected}
          className="hidden"
          aria-label="Upload attachment"
        />
        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          disabled={uploadAttachment.isPending}
          className="rounded-md border border-slate-300 px-3 py-1 text-xs font-medium text-slate-700 transition hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-60 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
        >
          {uploadAttachment.isPending ? 'Uploading…' : 'Upload file'}
        </button>
      </div>

      {uploadAttachment.isError && (
        <p className="text-xs text-red-600 dark:text-red-400" role="alert">
          {extractApiErrorMessage(uploadAttachment.error)}
        </p>
      )}
    </div>
  );
}
