import { useState } from 'react';
import { useCreateSubtask, useDeleteSubtask, useUpdateSubtask } from '@/features/tasks/hooks';
import type { SubTask } from '@/features/tasks/types';

interface SubtaskListProps {
  taskId: string;
  subtasks: SubTask[];
}

export function SubtaskList({ taskId, subtasks }: SubtaskListProps) {
  const [newTitle, setNewTitle] = useState('');
  const createSubtask = useCreateSubtask();
  const updateSubtask = useUpdateSubtask();
  const deleteSubtask = useDeleteSubtask();

  const handleAdd = (event: React.FormEvent) => {
    event.preventDefault();
    const title = newTitle.trim();
    if (!title) return;

    createSubtask.mutate(
      { taskId, payload: { title, order: subtasks.length } },
      { onSuccess: () => setNewTitle('') }
    );
  };

  return (
    <div className="space-y-2">
      {subtasks.length > 0 && (
        <ul className="space-y-1">
          {subtasks.map((subtask) => (
            <li key={subtask.id} className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={subtask.is_completed}
                onChange={(event) =>
                  updateSubtask.mutate({
                    taskId,
                    subtaskId: subtask.id,
                    payload: { is_completed: event.target.checked },
                  })
                }
                className="h-4 w-4 rounded border-slate-300 text-brand-600 focus:ring-brand-500"
                aria-label={subtask.title}
              />
              <span
                className={`flex-1 text-sm ${
                  subtask.is_completed
                    ? 'text-slate-400 line-through'
                    : 'text-slate-700 dark:text-slate-300'
                }`}
              >
                {subtask.title}
              </span>
              <button
                type="button"
                onClick={() => deleteSubtask.mutate({ taskId, subtaskId: subtask.id })}
                className="text-xs text-slate-400 hover:text-red-600 dark:hover:text-red-400"
                aria-label={`Remove ${subtask.title}`}
              >
                Remove
              </button>
            </li>
          ))}
        </ul>
      )}

      <form onSubmit={handleAdd} className="flex gap-2">
        <input
          type="text"
          value={newTitle}
          onChange={(event) => setNewTitle(event.target.value)}
          placeholder="Add a subtask"
          className="flex-1 rounded-md border border-slate-300 bg-white px-2 py-1 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-500/30 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
        />
        <button
          type="submit"
          disabled={!newTitle.trim() || createSubtask.isPending}
          className="rounded-md border border-slate-300 px-3 py-1 text-sm font-medium text-slate-700 transition hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-60 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
        >
          Add
        </button>
      </form>
    </div>
  );
}
