import { useDeleteReminder, useReminders } from '@/features/reminders/hooks';

function formatRemindAt(value: string): string {
  return new Date(value).toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  });
}

export function ReminderList() {
  const { data, isLoading, isError } = useReminders({ is_sent: false });
  const deleteReminder = useDeleteReminder();

  if (isLoading) {
    return <p className="text-sm text-slate-500 dark:text-slate-400">Loading reminders…</p>;
  }

  if (isError) {
    return <p className="text-sm text-red-600 dark:text-red-400">Couldn&apos;t load reminders.</p>;
  }

  if (!data || data.results.length === 0) {
    return <p className="text-sm text-slate-500 dark:text-slate-400">No upcoming reminders yet.</p>;
  }

  return (
    <ul className="flex flex-col gap-2">
      {data.results.map((reminder) => (
        <li
          key={reminder.id}
          className="flex items-center justify-between gap-3 rounded-md border border-slate-200 bg-white px-3 py-2 dark:border-slate-700 dark:bg-slate-800"
        >
          <div className="min-w-0">
            <p className="truncate text-sm text-slate-900 dark:text-slate-100">{reminder.title}</p>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              {formatRemindAt(reminder.remind_at)}
              {reminder.task && ` · ${reminder.task.title}`}
              {reminder.event && ` · ${reminder.event.title}`}
            </p>
          </div>
          <button
            type="button"
            onClick={() => deleteReminder.mutate(reminder.id)}
            className="shrink-0 text-xs font-medium text-slate-500 hover:text-red-600 dark:text-slate-400 dark:hover:text-red-400"
          >
            Delete
          </button>
        </li>
      ))}
    </ul>
  );
}
