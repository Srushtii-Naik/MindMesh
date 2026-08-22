import { ProductivityChart } from '@/features/analytics/components/ProductivityChart';
import { useProductivityAnalytics } from '@/features/analytics/hooks';

/**
 * ROADMAP.md Milestone 11 checklist: "Productivity analytics computed
 * accurately from task/calendar data." Backed by GET /analytics/productivity/.
 */
export function ProductivitySummaryCard() {
  const { data, isLoading, isError } = useProductivityAnalytics(30);

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
      <h3 className="text-sm font-medium text-slate-700 dark:text-slate-300">
        Productivity — last 30 days
      </h3>

      {isLoading && <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">Loading…</p>}

      {isError && (
        <p className="mt-2 text-sm text-red-600 dark:text-red-400">
          Couldn&apos;t load productivity analytics.
        </p>
      )}

      {data && (
        <>
          <dl className="mt-2 grid grid-cols-2 gap-3 sm:grid-cols-4">
            <div>
              <dt className="text-xs text-slate-500 dark:text-slate-400">Completed</dt>
              <dd className="text-lg font-semibold text-slate-900 dark:text-slate-100">
                {data.tasks_completed}
              </dd>
            </div>
            <div>
              <dt className="text-xs text-slate-500 dark:text-slate-400">Created</dt>
              <dd className="text-lg font-semibold text-slate-900 dark:text-slate-100">
                {data.tasks_created}
              </dd>
            </div>
            <div>
              <dt className="text-xs text-slate-500 dark:text-slate-400">Completion rate</dt>
              <dd className="text-lg font-semibold text-slate-900 dark:text-slate-100">
                {data.completion_rate}%
              </dd>
            </div>
            <div>
              <dt className="text-xs text-slate-500 dark:text-slate-400">Notes / Events</dt>
              <dd className="text-lg font-semibold text-slate-900 dark:text-slate-100">
                {data.notes_created} / {data.events_scheduled}
              </dd>
            </div>
          </dl>

          <div className="mt-4">
            <ProductivityChart series={data.daily_series} />
          </div>
        </>
      )}
    </div>
  );
}
