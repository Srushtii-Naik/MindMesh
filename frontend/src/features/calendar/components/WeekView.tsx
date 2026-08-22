import { formatDayLabel, isToday } from '@/features/calendar/dateUtils';
import { useWeeklyPlanner } from '@/features/calendar/hooks';
import { EventItem } from '@/features/calendar/components/EventItem';
import { TaskDueItem } from '@/features/calendar/components/TaskDueItem';
import type { CalendarEvent, IsoDate } from '@/features/calendar/types';

interface WeekViewProps {
  weekStart: IsoDate;
  onEditEvent: (event: CalendarEvent) => void;
  onDeleteEvent: (eventId: string) => void;
  onSelectDay: (day: IsoDate) => void;
}

/** ROADMAP.md Milestone 5 — Weekly planner: a 7-day breakdown of events and due tasks. */
export function WeekView({ weekStart, onEditEvent, onDeleteEvent, onSelectDay }: WeekViewProps) {
  const { data, isLoading, isError } = useWeeklyPlanner(weekStart);

  if (isLoading) {
    return <p className="text-sm text-slate-500 dark:text-slate-400">Loading week…</p>;
  }

  if (isError || !data) {
    return (
      <p className="text-sm text-red-600 dark:text-red-400">
        Couldn&apos;t load the weekly planner.
      </p>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-7">
      {data.days.map((day) => (
        <div key={day.date} className="flex min-w-0 flex-col gap-2">
          <button
            type="button"
            onClick={() => onSelectDay(day.date)}
            className={`self-start rounded-md px-2 py-1 text-xs font-semibold transition hover:bg-slate-100 dark:hover:bg-slate-800 ${
              isToday(day.date)
                ? 'bg-brand-600 text-white hover:bg-brand-700'
                : 'text-slate-600 dark:text-slate-300'
            }`}
          >
            {formatDayLabel(day.date)}
          </button>

          <ul className="flex flex-col gap-1.5">
            {day.events.map((event) => (
              <EventItem
                key={event.id}
                event={event}
                onEdit={onEditEvent}
                onDelete={onDeleteEvent}
              />
            ))}
            {day.tasks.map((task) => (
              <TaskDueItem key={task.id} task={task} />
            ))}
            {day.events.length === 0 && day.tasks.length === 0 && (
              <p className="text-xs text-slate-400">Nothing scheduled</p>
            )}
          </ul>
        </div>
      ))}
    </div>
  );
}
