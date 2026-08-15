import { formatFullDateLabel } from '@/features/calendar/dateUtils';
import { useDailyPlanner } from '@/features/calendar/hooks';
import { EventItem } from '@/features/calendar/components/EventItem';
import { TaskDueItem } from '@/features/calendar/components/TaskDueItem';
import type { CalendarEvent, IsoDate } from '@/features/calendar/types';

interface DayViewProps {
  date: IsoDate;
  onEditEvent: (event: CalendarEvent) => void;
  onDeleteEvent: (eventId: string) => void;
}

/** ROADMAP.md Milestone 5 — Daily planner: a single day's events and due tasks. */
export function DayView({ date, onEditEvent, onDeleteEvent }: DayViewProps) {
  const { data, isLoading, isError } = useDailyPlanner(date);

  if (isLoading) {
    return <p className="text-sm text-slate-500 dark:text-slate-400">Loading day…</p>;
  }

  if (isError || !data) {
    return (
      <p className="text-sm text-red-600 dark:text-red-400">
        Couldn&apos;t load the daily planner.
      </p>
    );
  }

  const hasItems = data.events.length > 0 || data.tasks.length > 0;

  return (
    <div className="flex flex-col gap-3">
      <h3 className="text-sm font-medium text-slate-700 dark:text-slate-300">
        {formatFullDateLabel(date)}
      </h3>

      {!hasItems && (
        <p className="text-sm text-slate-500 dark:text-slate-400">
          Nothing scheduled for this day.
        </p>
      )}

      {data.tasks.length > 0 && (
        <ul className="flex flex-col gap-2">
          {data.tasks.map((task) => (
            <TaskDueItem key={task.id} task={task} />
          ))}
        </ul>
      )}

      {data.events.length > 0 && (
        <ul className="flex flex-col gap-2">
          {data.events.map((event) => (
            <EventItem key={event.id} event={event} onEdit={onEditEvent} onDelete={onDeleteEvent} />
          ))}
        </ul>
      )}
    </div>
  );
}
