import { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { extractApiErrorMessage } from '@/api/errors';
import { useCreateEvent, useUpdateEvent } from '@/features/calendar/hooks';
import { useTasks } from '@/features/tasks';
import type { CalendarEvent, EventPayload } from '@/features/calendar/types';

interface EventFormValues {
  title: string;
  description: string;
  location: string;
  start_time: string;
  end_time: string;
  all_day: boolean;
  color: string;
  task_id: string;
}

const COLOR_OPTIONS = [
  { value: '#5f6dfa', label: 'Brand' },
  { value: '#16a34a', label: 'Green' },
  { value: '#dc2626', label: 'Red' },
  { value: '#d97706', label: 'Amber' },
  { value: '#0891b2', label: 'Teal' },
];

/** Converts an ISO timestamp to the value a `datetime-local` input expects. */
function toDatetimeLocalValue(isoString: string): string {
  const date = new Date(isoString);
  const offsetMs = date.getTimezoneOffset() * 60 * 1000;
  return new Date(date.getTime() - offsetMs).toISOString().slice(0, 16);
}

function defaultStartValue(initialDate?: string): string {
  const date = initialDate ? new Date(`${initialDate}T00:00:00`) : new Date();
  date.setMinutes(0, 0, 0);
  date.setHours(9);
  return toDatetimeLocalValue(date.toISOString());
}

function defaultEndValue(initialDate?: string): string {
  const date = initialDate ? new Date(`${initialDate}T00:00:00`) : new Date();
  date.setMinutes(0, 0, 0);
  date.setHours(10);
  return toDatetimeLocalValue(date.toISOString());
}

function toFormValues(event?: CalendarEvent, initialDate?: string): EventFormValues {
  return {
    title: event?.title ?? '',
    description: event?.description ?? '',
    location: event?.location ?? '',
    start_time: event ? toDatetimeLocalValue(event.start_time) : defaultStartValue(initialDate),
    end_time: event ? toDatetimeLocalValue(event.end_time) : defaultEndValue(initialDate),
    all_day: event?.all_day ?? false,
    color: event?.color ?? '#5f6dfa',
    task_id: event?.task?.id ?? '',
  };
}

interface EventFormProps {
  event?: CalendarEvent;
  initialDate?: string;
  onDone: () => void;
}

/** Create/edit form for a calendar event (ROADMAP.md Milestone 5). */
export function EventForm({ event, initialDate, onDone }: EventFormProps) {
  const { data: taskPages } = useTasks({ is_completed: false });
  const createEvent = useCreateEvent();
  const updateEvent = useUpdateEvent();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isDirty },
  } = useForm<EventFormValues>({ defaultValues: toFormValues(event, initialDate) });

  useEffect(() => {
    reset(toFormValues(event, initialDate));
  }, [event, initialDate, reset]);

  const isSaving = createEvent.isPending || updateEvent.isPending;
  const saveError = createEvent.error ?? updateEvent.error;

  const onSubmit = (values: EventFormValues) => {
    const payload: EventPayload = {
      title: values.title,
      description: values.description,
      location: values.location,
      start_time: new Date(values.start_time).toISOString(),
      end_time: new Date(values.end_time).toISOString(),
      all_day: values.all_day,
      color: values.color,
      task_id: values.task_id || null,
    };

    const mutation = event
      ? updateEvent.mutateAsync({ eventId: event.id, payload })
      : createEvent.mutateAsync(payload);

    mutation.then(onDone).catch(() => {
      /* surfaced via saveError below */
    });
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-4">
      <div>
        <label
          htmlFor="event-title"
          className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300"
        >
          Title
        </label>
        <input
          id="event-title"
          type="text"
          className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-500/30 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
          {...register('title', { required: 'Title is required.' })}
        />
        {errors.title && (
          <p className="mt-1 text-xs text-red-600 dark:text-red-400">{errors.title.message}</p>
        )}
      </div>

      <div>
        <label
          htmlFor="event-description"
          className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300"
        >
          Description
        </label>
        <textarea
          id="event-description"
          rows={2}
          className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-500/30 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
          {...register('description')}
        />
      </div>

      <div>
        <label
          htmlFor="event-location"
          className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300"
        >
          Location
        </label>
        <input
          id="event-location"
          type="text"
          className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-500/30 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
          {...register('location')}
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label
            htmlFor="event-start"
            className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300"
          >
            Starts
          </label>
          <input
            id="event-start"
            type="datetime-local"
            className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-500/30 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
            {...register('start_time', { required: 'Start time is required.' })}
          />
        </div>

        <div>
          <label
            htmlFor="event-end"
            className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300"
          >
            Ends
          </label>
          <input
            id="event-end"
            type="datetime-local"
            className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-500/30 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
            {...register('end_time', { required: 'End time is required.' })}
          />
        </div>
      </div>

      <label className="flex items-center gap-2 text-sm text-slate-700 dark:text-slate-300">
        <input
          type="checkbox"
          className="h-4 w-4 rounded border-slate-300 text-brand-600 focus:ring-brand-500"
          {...register('all_day')}
        />
        All day
      </label>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label
            htmlFor="event-color"
            className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300"
          >
            Color
          </label>
          <select
            id="event-color"
            className="w-full rounded-md border border-slate-300 bg-white px-2 py-2 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-500/30 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
            {...register('color')}
          >
            {COLOR_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label
            htmlFor="event-task"
            className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300"
          >
            Linked task
          </label>
          <select
            id="event-task"
            className="w-full rounded-md border border-slate-300 bg-white px-2 py-2 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-500/30 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
            {...register('task_id')}
          >
            <option value="">No linked task</option>
            {taskPages?.results.map((option) => (
              <option key={option.id} value={option.id}>
                {option.title}
              </option>
            ))}
          </select>
        </div>
      </div>

      {saveError && (
        <p className="text-sm text-red-600 dark:text-red-400" role="alert">
          {extractApiErrorMessage(saveError)}
        </p>
      )}

      <div className="flex justify-end gap-2">
        <button
          type="button"
          onClick={onDone}
          className="rounded-md border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={(!isDirty && Boolean(event)) || isSaving}
          className="rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isSaving ? 'Saving…' : event ? 'Save changes' : 'Create event'}
        </button>
      </div>
    </form>
  );
}
