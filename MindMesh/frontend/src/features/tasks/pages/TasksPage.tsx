import { useState } from 'react';
import { TaskSuggestions } from '@/features/tasks/components/TaskSuggestions';
import { TaskFilterBar } from '@/features/tasks/components/TaskFilterBar';
import { TaskList } from '@/features/tasks/components/TaskList';
import { TaskForm } from '@/features/tasks/components/TaskForm';
import { CategoryManager } from '@/features/tasks/components/CategoryManager';
import type { Task, TaskFilters } from '@/features/tasks/types';

/**
 * ROADMAP.md Milestone 4 — Task Management: the complete productivity
 * module (CRUD, subtasks, priorities, due dates, categories, recurrence,
 * and rule-based smart suggestions) in one page.
 */
export function TasksPage() {
  const [filters, setFilters] = useState<TaskFilters>({});
  const [editingTask, setEditingTask] = useState<Task | undefined>(undefined);
  const [isFormOpen, setIsFormOpen] = useState(false);

  const openCreateForm = () => {
    setEditingTask(undefined);
    setIsFormOpen(true);
  };

  const openEditForm = (task: Task) => {
    setEditingTask(task);
    setIsFormOpen(true);
  };

  const closeForm = () => {
    setIsFormOpen(false);
    setEditingTask(undefined);
  };

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6 px-4 py-8 sm:px-6 lg:px-8">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-brand-700 dark:text-brand-300">
            Tasks
          </h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Everything you need to do, in one place.
          </p>
        </div>
        {!isFormOpen && (
          <button
            type="button"
            onClick={openCreateForm}
            className="rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-brand-700"
          >
            New task
          </button>
        )}
      </header>

      <TaskSuggestions />

      {isFormOpen && (
        <section className="rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
          <h2 className="mb-3 text-sm font-medium text-slate-700 dark:text-slate-300">
            {editingTask ? 'Edit task' : 'New task'}
          </h2>
          <TaskForm task={editingTask} onDone={closeForm} />
        </section>
      )}

      <CategoryManager />

      <TaskFilterBar filters={filters} onChange={setFilters} />

      <TaskList filters={filters} onEdit={openEditForm} />
    </div>
  );
}
