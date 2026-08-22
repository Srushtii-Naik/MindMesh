import { useForm } from 'react-hook-form';
import { extractApiErrorMessage } from '@/api/errors';
import { useCreateReminder } from '@/features/reminders/hooks';
import type { ReminderPayload } from '@/features/reminders/types';

interface ReminderFormValues {
  title: string;
  remind_at: string;
}

function toDatetimeLocalValue(date: Date): string {
  const offsetMs = date.getTimezoneOffset() * 60 * 1000;
  return new Date(date.getTime() - offsetMs).toISOString().slice(0, 16);
}

function defaultRemindAt(): string {
  const date = new Date();
  date.setMinutes(0, 0, 0);
  date.setHours(date.getHours() + 1);
  return toDatetimeLocalValue(date);
}

/** Quick reminder creation (ROADMAP.md Milestone 5: reminder data model + CRUD). */
export function ReminderForm() {
  const createReminder = useCreateReminder();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ReminderFormValues>({
    defaultValues: { title: '', remind_at: defaultRemindAt() },
  });

  const onSubmit = (values: ReminderFormValues) => {
    const payload: ReminderPayload = {
      title: values.title,
      remind_at: new Date(values.remind_at).toISOString(),
    };

    createReminder.mutateAsync(payload).then(() => {
      reset({ title: '', remind_at: defaultRemindAt() });
    });
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate className="flex flex-wrap items-end gap-2">
      <div className="min-w-[10rem] flex-1">
        <label
          htmlFor="reminder-title"
          className="mb-1 block text-xs font-medium text-slate-700 dark:text-slate-300"
        >
          New reminder
        </label>
        <input
          id="reminder-title"
          type="text"
          placeholder="Take medication"
          className="w-full rounded-md border border-slate-300 bg-white px-3 py-1.5 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-500/30 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
          {...register('title', { required: 'Title is required.' })}
        />
      </div>

      <div>
        <label
          htmlFor="reminder-remind-at"
          className="mb-1 block text-xs font-medium text-slate-700 dark:text-slate-300"
        >
          Remind at
        </label>
        <input
          id="reminder-remind-at"
          type="datetime-local"
          className="rounded-md border border-slate-300 bg-white px-3 py-1.5 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-500/30 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
          {...register('remind_at', { required: 'Remind time is required.' })}
        />
      </div>

      <button
        type="submit"
        disabled={createReminder.isPending}
        className="rounded-md bg-brand-600 px-4 py-1.5 text-sm font-medium text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {createReminder.isPending ? 'Adding…' : 'Add'}
      </button>

      {(errors.title || errors.remind_at || createReminder.isError) && (
        <p className="w-full text-xs text-red-600 dark:text-red-400" role="alert">
          {errors.title?.message ??
            errors.remind_at?.message ??
            extractApiErrorMessage(createReminder.error)}
        </p>
      )}
    </form>
  );
}
