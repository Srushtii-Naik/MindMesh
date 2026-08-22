import { Link } from 'react-router-dom';
import { addDays, formatDayLabel, toIsoDate } from '@/features/calendar/dateUtils';
import { useCalendarView } from '@/features/calendar';
import { ROUTES } from '@/constants';

/**
 * ROADMAP.md Milestone 5 checklist: dashboard's "Upcoming events preview"
 * graduates off PlaceholderCard now that Calendar & Scheduling has real
 * event data. Shows the next 7 days' events.
 */
export function UpcomingEventsCard() {
  const today = toIsoDate(new Date());
  const weekAhead = addDays(today, 6);
  const { data, isLoading, isError } = useCalendarView(today, weekAhead);

  const upcoming = [...(data?.events ?? [])]
    .sort((a, b) => a.start_time.localeCompare(b.start_time))
    .slice(0, 5);

  return (
    <div className="flex h-full flex-col gap-2 rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
      <h3 className="text-sm font-medium text-slate-700 dark:text-slate-300">Upcoming events</h3>

      {isLoading && <p className="text-sm text-slate-500 dark:text-slate-400">Loading…</p>}

      {isError && (
        <p className="text-sm text-red-600 dark:text-red-400">Couldn&apos;t load your events.</p>
      )}

      {data && upcoming.length === 0 && (
        <p className="text-sm text-slate-500 dark:text-slate-400">
          Nothing on your calendar this week.
        </p>
      )}

      {upcoming.length > 0 && (
        <ul className="space-y-1.5 text-sm text-slate-600 dark:text-slate-300">
          {upcoming.map((event) => (
            <li key={event.id} className="flex items-center gap-2">
              <span
                className="h-2 w-2 shrink-0 rounded-full"
                style={{ backgroundColor: event.color }}
                aria-hidden="true"
              />
              <span className="truncate">{event.title}</span>
              <span className="ml-auto shrink-0 text-xs text-slate-400">
                {formatDayLabel(toIsoDate(new Date(event.start_time)))}
              </span>
            </li>
          ))}
        </ul>
      )}

      <Link
        to={ROUTES.CALENDAR}
        className="mt-auto text-xs font-medium text-brand-600 hover:underline dark:text-brand-400"
      >
        View calendar
      </Link>
    </div>
  );
}
