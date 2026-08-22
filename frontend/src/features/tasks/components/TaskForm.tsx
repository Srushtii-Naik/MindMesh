import { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { extractApiErrorMessage } from '@/api/errors';
import { useCategories, useCreateTask, useUpdateTask } from '@/features/tasks/hooks';
import type { Priority, RecurrenceRule, Task, TaskPayload } from '@/features/tasks/types';

interface TaskFormValues {
  title: string;
  description: string;
  category_id: string;
  priority: Priority;
  due_date: string;
  recurrence: RecurrenceRule;
  recurrence_interval: number;
}

const PRIORITY_OPTIONS: { value: Priority; label: string }[] = [
  { value: 'low', label: 'Low' },
  { value: 'medium', label: 'Medium' },
  { value: 'high', label: 'High' },
  { value: 'urgent', label: 'Urgent' },
];

const RECURRENCE_OPTIONS: { value: RecurrenceRule; label: string }[] = [
  { value: 'none', label: 'Does not repeat' },
  { value: 'daily', label: 'Daily' },
  { value: 'weekly', label: 'Weekly' },
  { value: 'monthly', label: 'Monthly' },
];

function toFormValues(task?: Task): TaskFormValues {
  return {
    title: task?.title ?? '',
    description: task?.description ?? '',
    category_id: task?.category?.id ?? '',
    priority: task?.priority ?? 'medium',
    due_date: task?.due_date ?? '',
    recurrence: task?.recurrence ?? 'none',
    recurrence_interval: task?.recurrence_interval ?? 1,
  };
}

interface TaskFormProps {
  task?: Task;
  onDone: () => void;
}

/** Create/edit form for a task (ROADMAP.md Milestone 4). Used for both new and existing tasks. */
export function TaskForm({ task, onDone }: TaskFormProps) {
  const { data: categories } = useCategories();
  const createTask = useCreateTask();
  const updateTask = useUpdateTask();

  const {
    register,
    handleSubmit,
    reset,
    watch,
    formState: { errors, isDirty },
  } = useForm<TaskFormValues>({ defaultValues: toFormValues(task) });

  useEffect(() => {
    reset(toFormValues(task));
  }, [task, reset]);

  const recurrence = watch('recurrence');
  const isSaving = createTask.isPending || updateTask.isPending;
  const saveError = createTask.error ?? updateTask.error;

  const onSubmit = (values: TaskFormValues) => {
    const payload: TaskPayload = {
      title: values.title,
      description: values.description,
      category_id: values.category_id || null,
      priority: values.priority,
      due_date: values.due_date || null,
      recurrence: values.recurrence,
      recurrence_interval: values.recurrence === 'none' ? 1 : values.recurrence_interval,
    };

    const mutation = task
      ? updateTask.mutateAsync({ taskId: task.id, payload })
      : createTask.mutateAsync(payload);

    mutation.then(onDone).catch(() => {
      /* surfaced via saveError below */
    });
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-4">
      <div>
        <label
          htmlFor="title"
          className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300"
        >
          Title
        </label>
        <input
          id="title"
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
          htmlFor="description"
          className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300"
        >
          Description
        </label>
        <textarea
          id="description"
          rows={3}
          className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-500/30 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
          {...register('description')}
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label
            htmlFor="priority"
            className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300"
          >
            Priority
          </label>
          <select
            id="priority"
            className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-500/30 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
            {...register('priority')}
          >
            {PRIORITY_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label
            htmlFor="due_date"
            className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300"
          >
            Due date
          </label>
          <input
            id="due_date"
            type="date"
            className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-500/30 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
            {...register('due_date')}
          />
        </div>
      </div>

      <div>
        <label
          htmlFor="category_id"
          className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300"
        >
          Category
        </label>
        <select
          id="category_id"
          className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-500/30 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
          {...register('category_id')}
        >
          <option value="">No category</option>
          {categories?.map((option) => (
            <option key={option.id} value={option.id}>
              {option.name}
            </option>
          ))}
        </select>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label
            htmlFor="recurrence"
            className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300"
          >
            Repeats
          </label>
          <select
            id="recurrence"
            className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-500/30 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
            {...register('recurrence')}
          >
            {RECURRENCE_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        {recurrence !== 'none' && (
          <div>
            <label
              htmlFor="recurrence_interval"
              className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300"
            >
              Every
            </label>
            <input
              id="recurrence_interval"
              type="number"
              min={1}
              className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-500/30 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
              {...register('recurrence_interval', { valueAsNumber: true, min: 1 })}
            />
          </div>
        )}
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
          disabled={(!isDirty && Boolean(task)) || isSaving}
          className="rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isSaving ? 'Saving…' : task ? 'Save changes' : 'Create task'}
        </button>
      </div>
    </form>
  );
}
