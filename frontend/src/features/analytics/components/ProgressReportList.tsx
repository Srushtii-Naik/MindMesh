import { useProgressReports } from '@/features/analytics/hooks';

/**
 * ROADMAP.md Milestone 11 checklist: "Progress reports generated on a
 * sensible cadence (e.g., weekly)." Reports are produced automatically by
 * the weekly Celery Beat task (apps.analytics.tasks.generate_weekly_reports_task)
 * — this view is read-only history, not a "generate" trigger.
 */
export function ProgressReportList() {
  const { data: reports, isLoading, isError } = useProgressReports();

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
      <h3 className="text-sm font-medium text-slate-700 dark:text-slate-300">
        Weekly progress reports
      </h3>

      {isLoading && <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">Loading…</p>}

      {isError && (
        <p className="mt-2 text-sm text-red-600 dark:text-red-400">
          Couldn&apos;t load progress reports.
        </p>
      )}

      {reports && reports.length === 0 && (
        <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
          Your first weekly report will appear here once a full week of activity has passed.
        </p>
      )}

      {reports && reports.length > 0 && (
        <ul className="mt-2 divide-y divide-slate-100 dark:divide-slate-700">
          {reports.map((report) => (
            <li key={report.id} className="py-3 first:pt-0 last:pb-0">
              <p className="text-sm font-medium text-slate-800 dark:text-slate-200">
                {report.period_start} – {report.period_end}
              </p>
              <p className="mt-0.5 text-xs text-slate-500 dark:text-slate-400">
                {report.tasks_completed} of {report.tasks_created} tasks completed (
                {report.completion_rate}%) · longest streak {report.longest_streak_days} day
                {report.longest_streak_days === 1 ? '' : 's'}
              </p>
              {report.ai_summary && (
                <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">
                  {report.ai_summary}
                </p>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
