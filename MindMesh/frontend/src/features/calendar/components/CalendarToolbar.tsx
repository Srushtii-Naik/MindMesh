import type { CalendarViewMode } from '@/features/calendar/types';

const VIEW_OPTIONS: { value: CalendarViewMode; label: string }[] = [
  { value: 'month', label: 'Month' },
  { value: 'week', label: 'Week' },
  { value: 'day', label: 'Day' },
];

interface CalendarToolbarProps {
  label: string;
  viewMode: CalendarViewMode;
  onViewModeChange: (mode: CalendarViewMode) => void;
  onPrevious: () => void;
  onNext: () => void;
  onToday: () => void;
  onCreateEvent: () => void;
}

export function CalendarToolbar({
  label,
  viewMode,
  onViewModeChange,
  onPrevious,
  onNext,
  onToday,
  onCreateEvent,
}: CalendarToolbarProps) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-3">
      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={onPrevious}
          aria-label="Previous"
          className="rounded-md border border-slate-300 px-2.5 py-1.5 text-sm text-slate-600 transition hover:bg-slate-100 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
        >
          ‹
        </button>
        <button
          type="button"
          onClick={onToday}
          className="rounded-md border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-700 transition hover:bg-slate-100 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
        >
          Today
        </button>
        <button
          type="button"
          onClick={onNext}
          aria-label="Next"
          className="rounded-md border border-slate-300 px-2.5 py-1.5 text-sm text-slate-600 transition hover:bg-slate-100 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
        >
          ›
        </button>
        <h2 className="ml-2 text-sm font-medium text-slate-700 dark:text-slate-300">{label}</h2>
      </div>

      <div className="flex items-center gap-2">
        <div
          role="group"
          aria-label="Calendar view"
          className="flex rounded-md border border-slate-300 dark:border-slate-700"
        >
          {VIEW_OPTIONS.map((option, index) => (
            <button
              key={option.value}
              type="button"
              onClick={() => onViewModeChange(option.value)}
              aria-pressed={viewMode === option.value}
              className={`px-3 py-1.5 text-sm font-medium transition ${
                index > 0 ? 'border-l border-slate-300 dark:border-slate-700' : ''
              } ${
                viewMode === option.value
                  ? 'bg-brand-600 text-white'
                  : 'text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800'
              }`}
            >
              {option.label}
            </button>
          ))}
        </div>

        <button
          type="button"
          onClick={onCreateEvent}
          className="rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-brand-700"
        >
          New event
        </button>
      </div>
    </div>
  );
}
