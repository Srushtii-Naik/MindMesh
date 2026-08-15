import { formatTimeLabel } from '@/features/calendar/dateUtils';
import type { CalendarEvent } from '@/features/calendar/types';

interface EventItemProps {
  event: CalendarEvent;
  onEdit: (event: CalendarEvent) => void;
  onDelete: (eventId: string) => void;
}

export function EventItem({ event, onEdit, onDelete }: EventItemProps) {
  return (
    <li className="rounded-lg border border-slate-200 bg-white p-3 dark:border-slate-700 dark:bg-slate-800">
      <div className="flex items-start gap-3">
        <span
          className="mt-1 h-2.5 w-2.5 shrink-0 rounded-full"
          style={{ backgroundColor: event.color }}
          aria-hidden="true"
        />

        <div className="min-w-0 flex-1">
          <p className="text-sm font-medium text-slate-900 dark:text-slate-100">{event.title}</p>
          <p className="mt-0.5 text-xs text-slate-500 dark:text-slate-400">
            {event.all_day
              ? 'All day'
              : `${formatTimeLabel(event.start_time)} – ${formatTimeLabel(event.end_time)}`}
            {event.location && ` · ${event.location}`}
          </p>
          {event.task && (
            <p className="mt-0.5 text-xs text-brand-600 dark:text-brand-400">
              Linked to task: {event.task.title}
            </p>
          )}
        </div>

        <div className="flex shrink-0 gap-2">
          <button
            type="button"
            onClick={() => onEdit(event)}
            className="text-xs font-medium text-slate-500 hover:text-brand-600 dark:text-slate-400 dark:hover:text-brand-400"
          >
            Edit
          </button>
          <button
            type="button"
            onClick={() => onDelete(event.id)}
            className="text-xs font-medium text-slate-500 hover:text-red-600 dark:text-slate-400 dark:hover:text-red-400"
          >
            Delete
          </button>
        </div>
      </div>
    </li>
  );
}
