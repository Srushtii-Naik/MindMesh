import { useCategories } from '@/features/tasks/hooks';
import type { Priority, TaskFilters } from '@/features/tasks/types';

const PRIORITY_OPTIONS: { value: Priority; label: string }[] = [
  { value: 'low', label: 'Low' },
  { value: 'medium', label: 'Medium' },
  { value: 'high', label: 'High' },
  { value: 'urgent', label: 'Urgent' },
];

interface TaskFilterBarProps {
  filters: TaskFilters;
  onChange: (filters: TaskFilters) => void;
}

export function TaskFilterBar({ filters, onChange }: TaskFilterBarProps) {
  const { data: categories } = useCategories();

  return (
    <div className="flex flex-wrap items-center gap-2">
      <input
        type="search"
        placeholder="Search tasks…"
        value={filters.search ?? ''}
        onChange={(event) => onChange({ ...filters, search: event.target.value || undefined })}
        className="w-48 rounded-md border border-slate-300 bg-white px-3 py-1.5 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-500/30 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
      />

      <select
        value={filters.priority ?? ''}
        onChange={(event) =>
          onChange({ ...filters, priority: (event.target.value as Priority) || undefined })
        }
        className="rounded-md border border-slate-300 bg-white px-2 py-1.5 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-500/30 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
      >
        <option value="">Any priority</option>
        {PRIORITY_OPTIONS.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>

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
        value={filters.is_completed === undefined ? '' : String(filters.is_completed)}
        onChange={(event) =>
          onChange({
            ...filters,
            is_completed: event.target.value === '' ? undefined : event.target.value === 'true',
          })
        }
        className="rounded-md border border-slate-300 bg-white px-2 py-1.5 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-500/30 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
      >
        <option value="">All tasks</option>
        <option value="false">Open</option>
        <option value="true">Completed</option>
      </select>
    </div>
  );
}
