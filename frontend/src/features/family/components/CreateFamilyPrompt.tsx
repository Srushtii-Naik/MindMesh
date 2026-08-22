import { useState } from 'react';
import {
  useAcceptInvitation,
  useCreateFamily,
  useDeclineInvitation,
  useMyInvitations,
} from '@/features/family/hooks';
import { extractApiErrorMessage } from '@/api/errors';

/**
 * Shown when the current user doesn't belong to a family yet (ROADMAP.md
 * Milestone 10). Lets them either start a new family or respond to a
 * pending invitation someone else sent them.
 */
export function CreateFamilyPrompt() {
  const [name, setName] = useState('');
  const [error, setError] = useState<string | null>(null);

  const createFamily = useCreateFamily();
  const { data: invitations, isLoading: invitationsLoading } = useMyInvitations();
  const acceptInvitation = useAcceptInvitation();
  const declineInvitation = useDeclineInvitation();

  function handleCreate(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    createFamily.mutate(name, {
      onError: (err) => setError(extractApiErrorMessage(err)),
    });
  }

  return (
    <section className="mx-auto flex max-w-lg flex-col gap-8 px-4 py-8 sm:px-6 lg:px-8">
      <div>
        <h1 className="text-lg font-semibold text-slate-900 dark:text-slate-100">Family</h1>
        <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">
          Start a family to share tasks, a calendar, notes, and emergency contacts with the people
          you trust.
        </p>
      </div>

      {!invitationsLoading && invitations && invitations.length > 0 && (
        <div className="flex flex-col gap-2">
          <h2 className="text-sm font-medium text-slate-700 dark:text-slate-300">
            Pending invitations
          </h2>
          <ul className="flex flex-col gap-2">
            {invitations.map((invitation) => (
              <li
                key={invitation.id}
                className="flex items-center justify-between gap-3 rounded-lg border border-slate-200 bg-white p-3 dark:border-slate-700 dark:bg-slate-800"
              >
                <div className="min-w-0">
                  <p className="truncate text-sm font-medium text-slate-900 dark:text-slate-100">
                    {invitation.family.name}
                  </p>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    Invited by {invitation.invited_by.full_name} as {invitation.role}
                  </p>
                </div>
                <div className="flex shrink-0 gap-2">
                  <button
                    type="button"
                    onClick={() => acceptInvitation.mutate(invitation.id)}
                    disabled={acceptInvitation.isPending}
                    className="rounded-md bg-brand-600 px-3 py-1 text-xs font-medium text-white transition hover:bg-brand-700 disabled:opacity-60"
                  >
                    Accept
                  </button>
                  <button
                    type="button"
                    onClick={() => declineInvitation.mutate(invitation.id)}
                    disabled={declineInvitation.isPending}
                    className="rounded-md border border-slate-300 px-3 py-1 text-xs font-medium text-slate-700 transition hover:bg-slate-100 disabled:opacity-60 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
                  >
                    Decline
                  </button>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      <form onSubmit={handleCreate} className="flex flex-col gap-3">
        <h2 className="text-sm font-medium text-slate-700 dark:text-slate-300">
          Or start a new family
        </h2>
        <input
          type="text"
          value={name}
          onChange={(event) => setName(event.target.value)}
          placeholder="e.g. The Does"
          className="rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
        />
        {error && <p className="text-sm text-red-600 dark:text-red-400">{error}</p>}
        <button
          type="submit"
          disabled={createFamily.isPending || !name.trim()}
          className="self-start rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-brand-700 disabled:opacity-60"
        >
          {createFamily.isPending ? 'Creating…' : 'Create family'}
        </button>
      </form>
    </section>
  );
}
