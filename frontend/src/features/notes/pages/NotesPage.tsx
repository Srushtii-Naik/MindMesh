import { useState } from 'react';
import { CategoryManager } from '@/features/notes/components/CategoryManager';
import { NoteFilterBar } from '@/features/notes/components/NoteFilterBar';
import { NoteForm } from '@/features/notes/components/NoteForm';
import { NoteList } from '@/features/notes/components/NoteList';
import { TagManager } from '@/features/notes/components/TagManager';
import type { Note, NoteFilters } from '@/features/notes/types';

/**
 * ROADMAP.md Milestone 6 — Notes & Knowledge: rich notes, categories, tags,
 * search, attachments, and AI summaries (via the AI abstraction layer) in
 * one page — mirroring features/tasks/pages/TasksPage.tsx's structure.
 */
export function NotesPage() {
  const [filters, setFilters] = useState<NoteFilters>({});
  const [editingNote, setEditingNote] = useState<Note | undefined>(undefined);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [isOrganizeOpen, setIsOrganizeOpen] = useState(false);

  const openCreateForm = () => {
    setEditingNote(undefined);
    setIsFormOpen(true);
  };

  const openEditForm = (note: Note) => {
    setEditingNote(note);
    setIsFormOpen(true);
  };

  const closeForm = () => {
    setIsFormOpen(false);
    setEditingNote(undefined);
  };

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6 px-4 py-8 sm:px-6 lg:px-8">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-brand-700 dark:text-brand-300">
            Notes
          </h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Capture and organize what matters.
          </p>
        </div>
        {!isFormOpen && (
          <button
            type="button"
            onClick={openCreateForm}
            className="rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-brand-700"
          >
            New note
          </button>
        )}
      </header>

      {isFormOpen && (
        <section className="rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
          <h2 className="mb-3 text-sm font-medium text-slate-700 dark:text-slate-300">
            {editingNote ? 'Edit note' : 'New note'}
          </h2>
          <NoteForm note={editingNote} onDone={closeForm} />
        </section>
      )}

      <section>
        <button
          type="button"
          onClick={() => setIsOrganizeOpen((value) => !value)}
          className="text-sm font-medium text-brand-600 hover:text-brand-700 dark:text-brand-400"
        >
          {isOrganizeOpen ? 'Hide categories & tags' : 'Manage categories & tags'}
        </button>
        {isOrganizeOpen && (
          <div className="mt-3 space-y-4 rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
            <CategoryManager />
            <TagManager />
          </div>
        )}
      </section>

      <NoteFilterBar filters={filters} onChange={setFilters} />

      <NoteList filters={filters} onEdit={openEditForm} />
    </div>
  );
}
