import { useAuthStore } from '@/features/auth';
import { useSharedEvents, useUnshareEvent } from '@/features/family/hooks';
import type { Family } from '@/features/family/types';

/**
 * Events shared within the family. View-only for non-owners this milestone
 * (see apps/family/services.py's scope note) — owners/sharers can unshare.
 */
export function SharedEventsPanel({ family }: { family: Family }) {
  const currentUserId = useAuthStore((state) => state.user?.id);
  const { data: sharedEvents, isLoading } = useSharedEvents(family.id);
  const unshareEvent = useUnshareEvent(family.id);

  return (
    <div>
      <h2 className="mb-3 text-sm font-medium text-slate-700 dark:text-slate-300">
        Shared calendar
      </h2>
      {isLoading && <p className="text-sm text-slate-500 dark:text-slate-400">Loading…</p>}
      {!isLoading && sharedEvents?.length === 0 && (
        <p className="text-sm text-slate-500 dark:text-slate-400">
          No events have been shared with your family yet.
        </p>
      )}
      <ul className="flex flex-col gap-2">
        {sharedEvents?.map(({ share, event }) => (
          <li
            key={share.id}
            className="flex items-start justify-between gap-3 rounded-lg border border-slate-200 bg-white p-3 dark:border-slate-700 dark:bg-slate-800"
          >
            <div className="min-w-0">
              <p className="truncate text-sm font-medium text-slate-900 dark:text-slate-100">
                {event.title}
              </p>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                {new Date(event.start_time).toLocaleString()} · Shared by{' '}
                {share.shared_by.full_name}
              </p>
            </div>
            {(share.owner.id === currentUserId || share.shared_by.id === currentUserId) && (
              <button
                type="button"
                onClick={() => unshareEvent.mutate(share.id)}
                className="shrink-0 text-xs font-medium text-slate-500 hover:text-red-600 dark:text-slate-400 dark:hover:text-red-400"
              >
                Unshare
              </button>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
