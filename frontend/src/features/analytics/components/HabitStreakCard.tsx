import { HabitHeatmap } from '@/features/analytics/components/HabitHeatmap';
import { useHabitTracking } from '@/features/analytics/hooks';

/**
 * ROADMAP.md Milestone 11 checklist: "Habit tracking implemented and
 * visualized clearly." Backed by GET /analytics/habits/.
 */
export function HabitStreakCard() {
  const { data, isLoading, isError } = useHabitTracking(90);

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
      <h3 className="text-sm font-medium text-slate-700 dark:text-slate-300">
        Daily task-completion streak
      </h3>

      {isLoading && <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">Loading…</p>}

      {isError && (
        <p className="mt-2 text-sm text-red-600 dark:text-red-400">
          Couldn&apos;t load habit tracking.
        </p>
      )}

      {data && (
        <>
          <dl className="mt-2 flex gap-6">
            <div>
              <dt className="text-xs text-slate-500 dark:text-slate-400">Current streak</dt>
              <dd className="text-lg font-semibold text-slate-900 dark:text-slate-100">
                {data.current_streak_days} day{data.current_streak_days === 1 ? '' : 's'}
              </dd>
            </div>
            <div>
              <dt className="text-xs text-slate-500 dark:text-slate-400">Longest streak</dt>
              <dd className="text-lg font-semibold text-slate-900 dark:text-slate-100">
                {data.longest_streak_days} day{data.longest_streak_days === 1 ? '' : 's'}
              </dd>
            </div>
          </dl>

          <div className="mt-4">
            <HabitHeatmap activity={data.daily_activity} />
          </div>
        </>
      )}
    </div>
  );
}
