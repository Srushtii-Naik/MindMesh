import { useState } from 'react';
import { extractApiErrorMessage } from '@/api/errors';
import { useCreateNoteCategory, useDeleteNoteCategory, useNoteCategories } from '@/features/notes/hooks';

const DEFAULT_COLOR = '#5f6dfa';

export function CategoryManager() {
  const { data: categories } = useNoteCategories();
  const createCategory = useCreateNoteCategory();
  const deleteCategory = useDeleteNoteCategory();
  const [name, setName] = useState('');

  const handleAdd = (event: React.FormEvent) => {
    event.preventDefault();
    const trimmed = name.trim();
    if (!trimmed) return;

    createCategory.mutate({ name: trimmed, color: DEFAULT_COLOR }, { onSuccess: () => setName('') });
  };

  return (
    <section aria-labelledby="note-categories-heading" className="space-y-2">
      <h2
        id="note-categories-heading"
        className="text-sm font-medium text-slate-700 dark:text-slate-300"
      >
        Categories
      </h2>

      {categories && categories.length > 0 && (
        <ul className="flex flex-wrap gap-2">
          {categories.map((category) => (
            <li
              key={category.id}
              className="flex items-center gap-1.5 rounded-full border border-slate-200 px-2 py-0.5 text-xs text-slate-600 dark:border-slate-700 dark:text-slate-300"
            >
              <span
                aria-hidden="true"
                className="h-2 w-2 rounded-full"
                style={{ backgroundColor: category.color }}
              />
              {category.name}
              <button
                type="button"
                onClick={() => deleteCategory.mutate(category.id)}
                aria-label={`Delete ${category.name}`}
                className="text-slate-400 hover:text-red-600 dark:hover:text-red-400"
              >
                ×
              </button>
            </li>
          ))}
        </ul>
      )}

      <form onSubmit={handleAdd} className="flex gap-2">
        <input
          type="text"
          value={name}
          onChange={(event) => setName(event.target.value)}
          placeholder="New category"
          className="w-40 rounded-md border border-slate-300 bg-white px-2 py-1 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-500/30 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
        />
        <button
          type="submit"
          disabled={!name.trim() || createCategory.isPending}
          className="rounded-md border border-slate-300 px-3 py-1 text-sm font-medium text-slate-700 transition hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-60 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
        >
          Add
        </button>
      </form>

      {createCategory.isError && (
        <p className="text-xs text-red-600 dark:text-red-400" role="alert">
          {extractApiErrorMessage(createCategory.error)}
        </p>
      )}
    </section>
  );
}
