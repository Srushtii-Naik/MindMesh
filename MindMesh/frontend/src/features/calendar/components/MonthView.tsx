import {
  addDays,
  endOfMonthGrid,
  fromIsoDate,
  isToday,
  startOfMonthGrid,
  toIsoDate,
} from '@/features/calendar/dateUtils';
import { useCalendarView } from '@/features/calendar/hooks';
import type { CalendarEvent, IsoDate } from '@/features/calendar/types';
import type { Task } from '@/features/tasks/types';

const WEEKDAY_LABELS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

interface MonthViewProps {
  monthAnchor: IsoDate;
  onSelectDay: (day: IsoDate) => void;
}

export function MonthView({ monthAnchor, onSelectDay }: MonthViewProps) {
  const gridStart = startOfMonthGrid(monthAnchor);
  const gridEnd = endOfMonthGrid(monthAnchor);
  const { data, isLoading, isError } = useCalendarView(gridStart, gridEnd);

  const days: IsoDate[] = [];
  for (let offset = 0; offset <= 41; offset += 1) {
    days.push(addDays(gridStart, offset));
  }

  const eventsByDay = new Map<IsoDate, CalendarEvent[]>();
  const tasksByDay = new Map<IsoDate, Task[]>();

  data?.events.forEach((event) => {
    const day = toIsoDate(new Date(event.start_time));
    eventsByDay.set(day, [...(eventsByDay.get(day) ?? []), event]);
  });
  data?.tasks.forEach((task) => {
    if (!task.due_date) return;
    tasksByDay.set(task.due_date, [...(tasksByDay.get(task.due_date) ?? []), task]);
  });

  const currentMonth = fromIsoDate(monthAnchor).getMonth();

  if (isLoading) {
    return <p className="text-sm text-slate-500 dark:text-slate-400">Loading calendar…</p>;
  }

  if (isError) {
    return (
      <p className="text-sm text-red-600 dark:text-red-400">Couldn&apos;t load the calendar.</p>
    );
  }

  return (
    <div className="overflow-hidden rounded-lg border border-slate-200 dark:border-slate-700">
      <div className="grid grid-cols-7 border-b border-slate-200 bg-slate-50 dark:border-slate-700 dark:bg-slate-900/40">
        {WEEKDAY_LABELS.map((label) => (
          <div
            key={label}
            className="px-2 py-2 text-center text-xs font-medium text-slate-500 dark:text-slate-400"
          >
            {label}
          </div>
        ))}
      </div>

      <div className="grid grid-cols-7">
        {days.map((day) => {
          const dayEvents = eventsByDay.get(day) ?? [];
          const dayTasks = tasksByDay.get(day) ?? [];
          const inCurrentMonth = fromIsoDate(day).getMonth() === currentMonth;
          const itemCount = dayEvents.length + dayTasks.length;

          return (
            <button
              key={day}
              type="button"
              onClick={() => onSelectDay(day)}
              className={`flex min-h-[88px] flex-col items-start gap-1 border-b border-r border-slate-200 p-2 text-left transition hover:bg-slate-50 dark:border-slate-700 dark:hover:bg-slate-800 ${
                inCurrentMonth ? '' : 'bg-slate-50/60 dark:bg-slate-900/20'
              }`}
            >
              <span
                className={`flex h-6 w-6 items-center justify-center rounded-full text-xs ${
                  isToday(day)
                    ? 'bg-brand-600 font-semibold text-white'
                    : inCurrentMonth
                      ? 'text-slate-700 dark:text-slate-300'
                      : 'text-slate-400 dark:text-slate-600'
                }`}
              >
                {fromIsoDate(day).getDate()}
              </span>

              <div className="flex w-full flex-col gap-0.5">
                {dayEvents.slice(0, 2).map((event) => (
                  <span
                    key={event.id}
                    className="truncate rounded px-1 py-0.5 text-[11px] text-white"
                    style={{ backgroundColor: event.color }}
                  >
                    {event.title}
                  </span>
                ))}
                {dayTasks.slice(0, Math.max(0, 2 - dayEvents.length)).map((task) => (
                  <span
                    key={task.id}
                    className="truncate rounded border border-amber-400 px-1 py-0.5 text-[11px] text-amber-700 dark:text-amber-400"
                  >
                    {task.title}
                  </span>
                ))}
                {itemCount > 2 && (
                  <span className="text-[11px] text-slate-400">+{itemCount - 2} more</span>
                )}
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
