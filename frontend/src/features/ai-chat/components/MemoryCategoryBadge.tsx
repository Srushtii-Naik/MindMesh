import type { MemoryCategory } from '@/features/ai-chat/types';

const CATEGORY_STYLES: Record<MemoryCategory, string> = {
  preference: 'bg-brand-50 text-brand-700 dark:bg-brand-900/30 dark:text-brand-300',
  important_date: 'bg-amber-50 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300',
  routine: 'bg-emerald-50 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300',
  relationship: 'bg-purple-50 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300',
  personal_fact: 'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300',
};

const CATEGORY_LABELS: Record<MemoryCategory, string> = {
  preference: 'Preference',
  important_date: 'Important date',
  routine: 'Routine',
  relationship: 'Relationship',
  personal_fact: 'Personal fact',
};

export function MemoryCategoryBadge({ category }: { category: MemoryCategory }) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${CATEGORY_STYLES[category]}`}
    >
      {CATEGORY_LABELS[category]}
    </span>
  );
}

export const MEMORY_CATEGORY_OPTIONS: { value: MemoryCategory; label: string }[] = (
  Object.keys(CATEGORY_LABELS) as MemoryCategory[]
).map((value) => ({ value, label: CATEGORY_LABELS[value] }));
