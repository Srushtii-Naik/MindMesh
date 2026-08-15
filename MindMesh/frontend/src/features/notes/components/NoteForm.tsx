import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { extractApiErrorMessage } from '@/api/errors';
import { useCreateNote, useNoteCategories, useNoteTags, useUpdateNote } from '@/features/notes/hooks';
import { NoteContentPreview } from '@/features/notes/markdown';
import type { Note, NotePayload } from '@/features/notes/types';

interface NoteFormValues {
  title: string;
  content: string;
  category_id: string;
  tag_ids: string[];
}

function toFormValues(note?: Note): NoteFormValues {
  return {
    title: note?.title ?? '',
    content: note?.content ?? '',
    category_id: note?.category?.id ?? '',
    tag_ids: note?.tags.map((tag) => tag.id) ?? [],
  };
}

interface NoteFormProps {
  note?: Note;
  onDone: () => void;
}

/** Create/edit form for a note (ROADMAP.md Milestone 6). Used for both new and existing notes. */
export function NoteForm({ note, onDone }: NoteFormProps) {
  const { data: categories } = useNoteCategories();
  const { data: tags } = useNoteTags();
  const createNote = useCreateNote();
  const updateNote = useUpdateNote();
  const [showPreview, setShowPreview] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    watch,
    formState: { errors, isDirty },
  } = useForm<NoteFormValues>({ defaultValues: toFormValues(note) });

  useEffect(() => {
    reset(toFormValues(note));
  }, [note, reset]);

  const content = watch('content');
  const isSaving = createNote.isPending || updateNote.isPending;
  const saveError = createNote.error ?? updateNote.error;

  const onSubmit = (values: NoteFormValues) => {
    const payload: NotePayload = {
      title: values.title,
      content: values.content,
      category_id: values.category_id || null,
      tag_ids: values.tag_ids,
    };

    const mutation = note
      ? updateNote.mutateAsync({ noteId: note.id, payload })
      : createNote.mutateAsync(payload);

    mutation.then(onDone).catch(() => {
      /* surfaced via saveError below */
    });
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-4">
      <div>
        <label htmlFor="title" className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">
          Title
        </label>
        <input
          id="title"
          type="text"
          className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-500/30 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
          {...register('title', { required: 'Title is required.' })}
        />
        {errors.title && (
          <p className="mt-1 text-xs text-red-600 dark:text-red-400">{errors.title.message}</p>
        )}
      </div>

      <div>
        <div className="mb-1 flex items-center justify-between">
          <label htmlFor="content" className="block text-sm font-medium text-slate-700 dark:text-slate-300">
            Content
          </label>
          <button
            type="button"
            onClick={() => setShowPreview((value) => !value)}
            className="text-xs font-medium text-brand-600 hover:text-brand-700 dark:text-brand-400"
          >
            {showPreview ? 'Edit' : 'Preview'}
          </button>
        </div>

        {showPreview ? (
          <div className="min-h-[10rem] rounded-md border border-slate-300 bg-white px-3 py-2 dark:border-slate-700 dark:bg-slate-800">
            <NoteContentPreview content={content} />
          </div>
        ) : (
          <>
            <textarea
              id="content"
              rows={8}
              placeholder="# Heading, **bold**, *italic*, - list item…"
              className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 font-mono text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-500/30 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
              {...register('content')}
            />
            <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
              Supports headings (#), bold (**text**), italic (*text*), and lists (- item).
            </p>
          </>
        )}
      </div>

      <div>
        <label
          htmlFor="category_id"
          className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300"
        >
          Category
        </label>
        <select
          id="category_id"
          className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-500/30 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
          {...register('category_id')}
        >
          <option value="">No category</option>
          {categories?.map((option) => (
            <option key={option.id} value={option.id}>
              {option.name}
            </option>
          ))}
        </select>
      </div>

      {tags && tags.length > 0 && (
        <fieldset>
          <legend className="mb-1 text-sm font-medium text-slate-700 dark:text-slate-300">Tags</legend>
          <div className="flex flex-wrap gap-3">
            {tags.map((tagOption) => (
              <label
                key={tagOption.id}
                className="flex items-center gap-1.5 text-sm text-slate-700 dark:text-slate-300"
              >
                <input
                  type="checkbox"
                  value={tagOption.id}
                  className="rounded border-slate-300 text-brand-600 focus:ring-brand-500/30 dark:border-slate-700"
                  {...register('tag_ids')}
                />
                #{tagOption.name}
              </label>
            ))}
          </div>
        </fieldset>
      )}

      {saveError && (
        <p className="text-sm text-red-600 dark:text-red-400" role="alert">
          {extractApiErrorMessage(saveError)}
        </p>
      )}

      <div className="flex justify-end gap-2">
        <button
          type="button"
          onClick={onDone}
          className="rounded-md border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={(!isDirty && Boolean(note)) || isSaving}
          className="rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isSaving ? 'Saving…' : note ? 'Save changes' : 'Create note'}
        </button>
      </div>
    </form>
  );
}
