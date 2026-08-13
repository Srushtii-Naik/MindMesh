import { useTasks } from '@/features/tasks/hooks';
import { TaskItem } from '@/features/tasks/components/TaskItem';
import type { Task, TaskFilters } from '@/features/tasks/types';

interface TaskListProps {
  filters: TaskFilters;
  onEdit: (task: Task) => void;
}

export function TaskList({ filters, onEdit }: TaskListProps) {
  const { data, isLoading, isError } = useTasks(filters);

  if (isLoading) {
    return <p className="text-sm text-slate-500 dark:text-slate-400">Loading tasks…</p>;
  }

  if (isError) {
    return <p className="text-sm text-red-600 dark:text-red-400">Couldn&apos;t load your tasks.</p>;
  }

  if (!data || data.results.length === 0) {
    return (
      <p className="text-sm text-slate-500 dark:text-slate-400">
        No tasks match these filters yet.
      </p>
    );
  }

  return (
    <ul className="space-y-2">
      {data.results.map((task) => (
        <TaskItem key={task.id} task={task} onEdit={onEdit} />
      ))}
    </ul>
  );
}
