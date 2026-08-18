import { useAuthStore } from '@/features/auth';
import { useCompleteSharedTask, useSharedTasks, useUnshareTask } from '@/features/family/hooks';
import type { Family } from '@/features/family/types';

/**
 * Tasks shared within the family (ROADMAP.md Milestone 10). Sharing itself
 * happens from the Tasks module (out of scope to duplicate here); this
 * panel is the family-wide view, and supports the "delegate tasks to my
 * children" flow (PRD.md Section 6.4) via complete/unshare when the
 * viewer has edit access.
 */
export function SharedTasksPanel({ family }: { family: Family }) {
  const currentUserId = useAuthStore((state) => state.user?.id);
  const { data: sharedTasks, isLoading } = useSharedTasks(family.id);
  const completeTask = useCompleteSharedTask(family.id);
  const unshareTask = useUnshareTask(family.id);

  return (
    <div>
      <h2 className="mb-3 text-sm font-medium text-slate-700 dark:text-slate-300">Shared tasks</h2>
      {isLoading && <p className="text-sm text-slate-500 dark:text-slate-400">Loading…</p>}
      {!isLoading && sharedTasks?.length === 0 && (
        <p className="text-sm text-slate-500 dark:text-slate-400">
          No tasks have been shared with your family yet.
        </p>
      )}
      <ul className="flex flex-col gap-2">
        {sharedTasks?.map(({ share, task }) => {
          const canAct = share.owner.id === currentUserId || share.can_edit;
          return (
            <li
              key={share.id}
              className="flex items-start justify-between gap-3 rounded-lg border border-slate-200 bg-white p-3 dark:border-slate-700 dark:bg-slate-800"
            >
              <div className="min-w-0">
                <p
                  className={`truncate text-sm font-medium ${
                    task.is_completed
                      ? 'text-slate-400 line-through dark:text-slate-500'
                      : 'text-slate-900 dark:text-slate-100'
                  }`}
                >
                  {task.title}
                </p>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Shared by {share.shared_by.full_name}
                  {share.owner.id !== share.shared_by.id && ` (owner: ${share.owner.full_name})`}
                  {' · '}
                  {share.can_edit ? 'Can edit' : 'View only'}
                </p>
              </div>
              <div className="flex shrink-0 items-center gap-2">
                {canAct && !task.is_completed && (
                  <button
                    type="button"
                    onClick={() => completeTask.mutate(share.id)}
                    className="text-xs font-medium text-brand-600 hover:underline dark:text-brand-400"
                  >
                    Mark done
                  </button>
                )}
                {(share.owner.id === currentUserId || share.shared_by.id === currentUserId) && (
                  <button
                    type="button"
                    onClick={() => unshareTask.mutate(share.id)}
                    className="text-xs font-medium text-slate-500 hover:text-red-600 dark:text-slate-400 dark:hover:text-red-400"
                  >
                    Unshare
                  </button>
                )}
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
