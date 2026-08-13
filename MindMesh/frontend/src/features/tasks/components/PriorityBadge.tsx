import type { Priority } from '@/features/tasks/types';

const PRIORITY_STYLES: Record<Priority, string> = {
  low: 'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300',
  medium: 'bg-brand-50 text-brand-700 dark:bg-brand-900/30 dark:text-brand-300',
  high: 'bg-amber-50 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300',
  urgent: 'bg-red-50 text-red-700 dark:bg-red-900/30 dark:text-red-300',
};

const PRIORITY_LABELS: Record<Priority, string> = {
  low: 'Low',
  medium: 'Medium',
  high: 'High',
  urgent: 'Urgent',
};

export function PriorityBadge({ priority }: { priority: Priority }) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${PRIORITY_STYLES[priority]}`}
    >
      {PRIORITY_LABELS[priority]}
    </span>
  );
}
