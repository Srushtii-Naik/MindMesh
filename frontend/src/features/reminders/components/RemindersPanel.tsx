import { ReminderForm } from '@/features/reminders/components/ReminderForm';
import { ReminderList } from '@/features/reminders/components/ReminderList';

/**
 * ROADMAP.md Milestone 5 — Reminders: foundational data model and CRUD.
 * Delivery (push/email/in-app) arrives in Milestone 9; this panel just lets
 * users create and manage the underlying reminder records.
 */
export function RemindersPanel() {
  return (
    <section
      aria-label="Reminders"
      className="flex flex-col gap-3 rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800"
    >
      <div>
        <h2 className="text-sm font-medium text-slate-700 dark:text-slate-300">Reminders</h2>
        <p className="text-xs text-slate-500 dark:text-slate-400">
          Reminders fire automatically and notify you in-app and by email (see Settings) once
          they&apos;re due.
        </p>
      </div>

      <ReminderForm />
      <ReminderList />
    </section>
  );
}
