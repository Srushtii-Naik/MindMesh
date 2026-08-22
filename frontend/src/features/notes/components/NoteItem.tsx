import { useState } from 'react';
import { extractApiErrorMessage } from '@/api/errors';
import { AttachmentList } from '@/features/notes/components/AttachmentList';
import { CategoryBadge } from '@/features/notes/components/CategoryBadge';
import { useDeleteNote, useGenerateNoteSummary } from '@/features/notes/hooks';
import { NoteContentPreview } from '@/features/notes/markdown';
import type { Note } from '@/features/notes/types';

function formatDate(value: string): string {
  return new Date(value).toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
}

interface NoteItemProps {
  note: Note;
  onEdit: (note: Note) => void;
}

export function NoteItem({ note, onEdit }: NoteItemProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const deleteNote = useDeleteNote();
  const generateSummary = useGenerateNoteSummary();

  return (
    <li className="rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
      <div className="flex items-start justify-between gap-3">
        <button
          type="button"
          onClick={() => setIsExpanded((value) => !value)}
          className="min-w-0 flex-1 text-left"
        >
          <span className="text-sm font-medium text-slate-900 dark:text-slate-100">{note.title}</span>
          <div className="mt-1.5 flex flex-wrap items-center gap-2">
            {note.category && <CategoryBadge category={note.category} />}
            {note.tags.map((tag) => (
              <span key={tag.id} className="text-xs text-slate-500 dark:text-slate-400">
                #{tag.name}
              </span>
            ))}
            <span className="text-xs text-slate-400">Updated {formatDate(note.updated_at)}</span>
            {note.attachments.length > 0 && (
              <span className="text-xs text-slate-400">
                📎 {note.attachments.length}
              </span>
            )}
          </div>
        </button>

        <div className="flex shrink-0 gap-2">
          <button
            type="button"
            onClick={() => onEdit(note)}
            className="text-xs font-medium text-slate-500 hover:text-brand-600 dark:text-slate-400 dark:hover:text-brand-400"
          >
            Edit
          </button>
          <button
            type="button"
            onClick={() => deleteNote.mutate(note.id)}
            className="text-xs font-medium text-slate-500 hover:text-red-600 dark:text-slate-400 dark:hover:text-red-400"
          >
            Delete
          </button>
        </div>
      </div>

      {isExpanded && (
        <div className="mt-3 space-y-4 border-t border-slate-100 pt-3 dark:border-slate-700">
          <NoteContentPreview content={note.content} />

          <div className="space-y-2 rounded-md bg-slate-50 p-3 dark:bg-slate-900/50">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-medium text-slate-700 dark:text-slate-300">AI Summary</h3>
              <button
                type="button"
                onClick={() => generateSummary.mutate(note.id)}
                disabled={generateSummary.isPending}
                className="text-xs font-medium text-brand-600 hover:text-brand-700 disabled:cursor-not-allowed disabled:opacity-60 dark:text-brand-400"
              >
                {generateSummary.isPending
                  ? 'Summarizing…'
                  : note.ai_summary
                    ? 'Regenerate'
                    : 'Generate summary'}
              </button>
            </div>
            {note.ai_summary ? (
              <p className="text-sm text-slate-600 dark:text-slate-300">{note.ai_summary}</p>
            ) : (
              <p className="text-sm italic text-slate-400 dark:text-slate-500">No summary yet.</p>
            )}
            {generateSummary.isError && (
              <p className="text-xs text-red-600 dark:text-red-400" role="alert">
                {extractApiErrorMessage(generateSummary.error)}
              </p>
            )}
          </div>

          <AttachmentList noteId={note.id} attachments={note.attachments} />
        </div>
      )}
    </li>
  );
}
