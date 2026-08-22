import { useRecentActivity } from '@/features/dashboard/hooks';
import type { ActivityItem } from '@/features/dashboard/types';

const MAX_ITEMS = 8;

function formatTimestamp(timestamp: string): string {
  return new Date(timestamp).toLocaleString(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  });
}

function ActivityRow({ item }: { item: ActivityItem }) {
  return (
    <li className="flex items-center justify-between gap-3 py-2 text-sm">
      <span className="text-slate-700 dark:text-slate-300">{item.label}</span>
      <span className="shrink-0 text-xs text-slate-400 dark:text-slate-500">
        {formatTimestamp(item.timestamp)}
      </span>
    </li>
  );
}

/**
 * ROADMAP.md Milestone 3: "Recent activity feed reflects real user
 * actions" — unlike the other cards, this checklist item has no
 * "placeholders otherwise" allowance, so it's built from data that
 * genuinely exists today (see hooks/useRecentActivity.ts).
 */
export function RecentActivityFeed() {
  const { items, isLoading, isError } = useRecentActivity();

  return (
    <section
      aria-labelledby="recent-activity-heading"
      className="rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800"
    >
      <h2
        id="recent-activity-heading"
        className="mb-2 text-sm font-medium text-slate-700 dark:text-slate-300"
      >
        Recent activity
      </h2>

      {isLoading && <p className="text-sm text-slate-500 dark:text-slate-400">Loading activity…</p>}

      {isError && (
        <p className="text-sm text-red-600 dark:text-red-400">Couldn&apos;t load your activity.</p>
      )}

      {!isLoading && !isError && items.length === 0 && (
        <p className="text-sm text-slate-500 dark:text-slate-400">No activity yet.</p>
      )}

      {!isLoading && !isError && items.length > 0 && (
        <ul className="divide-y divide-slate-100 dark:divide-slate-700">
          {items.slice(0, MAX_ITEMS).map((item) => (
            <ActivityRow key={item.id} item={item} />
          ))}
        </ul>
      )}
    </section>
  );
}
