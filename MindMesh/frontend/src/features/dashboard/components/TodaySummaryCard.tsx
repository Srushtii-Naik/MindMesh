import { Link } from 'react-router-dom';
import { useTodaySummary } from '@/features/tasks';
import { ROUTES } from '@/constants';

/**
 * ROADMAP.md Milestone 4 checklist: "Dashboard quick actions and 'Today's
 * Summary' reflect real task data." Backed by GET /tasks/summary/today/.
 */
export function TodaySummaryCard() {
  const { data: summary, isLoading, isError } = useTodaySummary();

  return (
    <div className="flex h-full flex-col gap-2 rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
      <h3 className="text-sm font-medium text-slate-700 dark:text-slate-300">
        Today&apos;s summary
      </h3>

      {isLoading && <p className="text-sm text-slate-500 dark:text-slate-400">Loading…</p>}

      {isError && (
        <p className="text-sm text-red-600 dark:text-red-400">
          Couldn&apos;t load today&apos;s summary.
        </p>
      )}

      {summary && (
        <>
          {summary.due_today_count === 0 && summary.overdue_count === 0 ? (
            <p className="text-sm text-slate-500 dark:text-slate-400">
              Nothing due today. Nice and clear.
            </p>
          ) : (
            <ul className="space-y-1 text-sm text-slate-600 dark:text-slate-300">
              {summary.due_today_count > 0 && (
                <li>
                  {summary.due_today_count} task{summary.due_today_count === 1 ? '' : 's'} due today
                </li>
              )}
              {summary.overdue_count > 0 && (
                <li className="text-amber-600 dark:text-amber-400">
                  {summary.overdue_count} overdue
                </li>
              )}
            </ul>
          )}
          {summary.completed_today_count > 0 && (
            <p className="text-xs text-slate-400">
              {summary.completed_today_count} completed today
            </p>
          )}
        </>
      )}

      <Link
        to={ROUTES.TASKS}
        className="mt-auto text-xs font-medium text-brand-600 hover:underline dark:text-brand-400"
      >
        View tasks
      </Link>
    </div>
  );
}
