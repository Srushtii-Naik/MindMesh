import { useState } from 'react';
import { useCompleteTask, useDeleteTask, useReopenTask } from '@/features/tasks/hooks';
import { PriorityBadge } from '@/features/tasks/components/PriorityBadge';
import { CategoryBadge } from '@/features/tasks/components/CategoryBadge';
import { SubtaskList } from '@/features/tasks/components/SubtaskList';
import type { Task } from '@/features/tasks/types';

function formatDueDate(dueDate: string | null): string | null {
  if (!dueDate) return null;
  return new Date(`${dueDate}T00:00:00`).toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
  });
}

interface TaskItemProps {
  task: Task;
  onEdit: (task: Task) => void;
}

export function TaskItem({ task, onEdit }: TaskItemProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const completeTask = useCompleteTask();
  const reopenTask = useReopenTask();
  const deleteTask = useDeleteTask();

  const dueLabel = formatDueDate(task.due_date);
  const completedSubtasks = task.subtasks.filter((subtask) => subtask.is_completed).length;

  return (
    <li className="rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
      <div className="flex items-start gap-3">
        <input
          type="checkbox"
          checked={task.is_completed}
          onChange={() =>
            task.is_completed ? reopenTask.mutate(task.id) : completeTask.mutate(task.id)
          }
          className="mt-1 h-4 w-4 rounded border-slate-300 text-brand-600 focus:ring-brand-500"
          aria-label={`Mark "${task.title}" ${task.is_completed ? 'incomplete' : 'complete'}`}
        />

        <div className="min-w-0 flex-1">
          <button
            type="button"
            onClick={() => setIsExpanded((value) => !value)}
            className="block w-full text-left"
          >
            <span
              className={`text-sm font-medium ${
                task.is_completed
                  ? 'text-slate-400 line-through'
                  : 'text-slate-900 dark:text-slate-100'
              }`}
            >
              {task.title}
            </span>
          </button>

          <div className="mt-1.5 flex flex-wrap items-center gap-2">
            <PriorityBadge priority={task.priority} />
            {task.category && <CategoryBadge category={task.category} />}
            {dueLabel && (
              <span className="text-xs text-slate-500 dark:text-slate-400">Due {dueLabel}</span>
            )}
            {task.recurrence !== 'none' && (
              <span className="text-xs text-slate-400">↻ {task.recurrence}</span>
            )}
            {task.subtasks.length > 0 && (
              <span className="text-xs text-slate-400">
                {completedSubtasks}/{task.subtasks.length} subtasks
              </span>
            )}
          </div>

          {isExpanded && (
            <div className="mt-3 space-y-3 border-t border-slate-100 pt-3 dark:border-slate-700">
              {task.description && (
                <p className="text-sm text-slate-600 dark:text-slate-300">{task.description}</p>
              )}
              <SubtaskList taskId={task.id} subtasks={task.subtasks} />
            </div>
          )}
        </div>

        <div className="flex shrink-0 gap-2">
          <button
            type="button"
            onClick={() => onEdit(task)}
            className="text-xs font-medium text-slate-500 hover:text-brand-600 dark:text-slate-400 dark:hover:text-brand-400"
          >
            Edit
          </button>
          <button
            type="button"
            onClick={() => deleteTask.mutate(task.id)}
            className="text-xs font-medium text-slate-500 hover:text-red-600 dark:text-slate-400 dark:hover:text-red-400"
          >
            Delete
          </button>
        </div>
      </div>
    </li>
  );
}
