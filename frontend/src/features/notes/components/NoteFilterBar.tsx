import { useNoteCategories, useNoteTags } from '@/features/notes/hooks';
import type { NoteFilters } from '@/features/notes/types';

interface NoteFilterBarProps {
  filters: NoteFilters;
  onChange: (filters: NoteFilters) => void;
}

export function NoteFilterBar({ filters, onChange }: NoteFilterBarProps) {
  const { data: categories } = useNoteCategories();
  const { data: tags } = useNoteTags();

  return (
    <div className="flex flex-wrap items-center gap-2">
      <input
        type="search"
        placeholder="Search notes…"
        value={filters.search ?? ''}
        onChange={(event) => onChange({ ...filters, search: event.target.value || undefined })}
        className="w-48 rounded-md border border-slate-300 bg-white px-3 py-1.5 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-500/30 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
      />

      <select
        value={filters.category_id ?? ''}
        onChange={(event) => onChange({ ...filters, category_id: event.target.value || undefined })}
        className="rounded-md border border-slate-300 bg-white px-2 py-1.5 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-500/30 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
      >
        <option value="">Any category</option>
        {categories?.map((category) => (
          <option key={category.id} value={category.id}>
            {category.name}
          </option>
        ))}
      </select>

      <select
        value={filters.tag_id ?? ''}
        onChange={(event) => onChange({ ...filters, tag_id: event.target.value || undefined })}
        className="rounded-md border border-slate-300 bg-white px-2 py-1.5 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-500/30 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
      >
        <option value="">Any tag</option>
        {tags?.map((tag) => (
          <option key={tag.id} value={tag.id}>
            #{tag.name}
          </option>
        ))}
      </select>
    </div>
  );
}
