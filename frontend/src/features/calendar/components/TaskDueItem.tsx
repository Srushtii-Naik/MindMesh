import { PriorityBadge } from '@/features/tasks/components/PriorityBadge';
import type { Task } from '@/features/tasks/types';

interface TaskDueItemProps {
  task: Task;
}

/** Read-only display of a task due date inside the calendar/planners — editing a task
 * happens on the Tasks page, per PROJECT_RULES.md (one owner per piece of data/UI). */
export function TaskDueItem({ task }: TaskDueItemProps) {
  return (
    <li className="rounded-lg border border-dashed border-slate-300 bg-slate-50 p-3 dark:border-slate-600 dark:bg-slate-900/40">
      <div className="flex items-start gap-3">
        <span
          className={`mt-1 h-2.5 w-2.5 shrink-0 rounded-full ${
            task.is_completed ? 'bg-slate-300 dark:bg-slate-600' : 'bg-amber-500'
          }`}
          aria-hidden="true"
        />
        <div className="min-w-0 flex-1">
          <p
            className={`text-sm font-medium ${
              task.is_completed
                ? 'text-slate-400 line-through'
                : 'text-slate-900 dark:text-slate-100'
            }`}
          >
            Task due: {task.title}
          </p>
          <div className="mt-0.5 flex items-center gap-2">
            <PriorityBadge priority={task.priority} />
          </div>
        </div>
      </div>
    </li>
  );
}
