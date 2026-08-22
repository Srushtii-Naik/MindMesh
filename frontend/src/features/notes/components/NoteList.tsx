import { NoteItem } from '@/features/notes/components/NoteItem';
import { useNotes } from '@/features/notes/hooks';
import type { Note, NoteFilters } from '@/features/notes/types';

interface NoteListProps {
  filters: NoteFilters;
  onEdit: (note: Note) => void;
}

export function NoteList({ filters, onEdit }: NoteListProps) {
  const { data, isLoading, isError } = useNotes(filters);

  if (isLoading) {
    return <p className="text-sm text-slate-500 dark:text-slate-400">Loading notes…</p>;
  }

  if (isError) {
    return <p className="text-sm text-red-600 dark:text-red-400">Couldn&apos;t load your notes.</p>;
  }

  if (!data || data.results.length === 0) {
    return (
      <p className="text-sm text-slate-500 dark:text-slate-400">
        No notes match these filters yet.
      </p>
    );
  }

  return (
    <ul className="space-y-2">
      {data.results.map((note) => (
        <NoteItem key={note.id} note={note} onEdit={onEdit} />
      ))}
    </ul>
  );
}
