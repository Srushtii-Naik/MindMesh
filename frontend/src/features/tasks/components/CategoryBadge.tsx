import type { Category } from '@/features/tasks/types';

export function CategoryBadge({ category }: { category: Category }) {
  return (
    <span className="inline-flex items-center gap-1.5 rounded-full border border-slate-200 px-2 py-0.5 text-xs font-medium text-slate-600 dark:border-slate-700 dark:text-slate-300">
      <span
        aria-hidden="true"
        className="h-2 w-2 rounded-full"
        style={{ backgroundColor: category.color }}
      />
      {category.name}
    </span>
  );
}
