import { useSessions, useRevokeAllSessions, useRevokeSession } from '@/features/auth/hooks';

function formatDate(iso: string): string {
  return new Date(iso).toLocaleString(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  });
}

export function SessionsList() {
  const { data: sessions, isLoading, isError } = useSessions();
  const revokeSession = useRevokeSession();
  const revokeAll = useRevokeAllSessions();

  if (isLoading) {
    return <p className="text-sm text-slate-500 dark:text-slate-400">Loading sessions…</p>;
  }

  if (isError || !sessions) {
    return (
      <p className="text-sm text-red-600 dark:text-red-400">Couldn&apos;t load your sessions.</p>
    );
  }

  return (
    <div className="space-y-4">
      <ul className="divide-y divide-slate-200 rounded-md border border-slate-200 dark:divide-slate-800 dark:border-slate-800">
        {sessions.length === 0 && (
          <li className="p-4 text-sm text-slate-500 dark:text-slate-400">No active sessions.</li>
        )}
        {sessions.map((session) => (
          <li key={session.id} className="flex items-center justify-between p-4">
            <div className="text-sm">
              <p className="text-slate-700 dark:text-slate-300">
                Signed in {formatDate(session.created_at)}
              </p>
              <p className="text-xs text-slate-400">Expires {formatDate(session.expires_at)}</p>
            </div>
            <button
              type="button"
              onClick={() => revokeSession.mutate(session.id)}
              disabled={revokeSession.isPending}
              className="rounded-md border border-slate-300 px-3 py-1 text-xs font-medium text-slate-600 transition hover:bg-slate-50 disabled:opacity-60 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
            >
              Sign out
            </button>
          </li>
        ))}
      </ul>

      {sessions.length > 0 && (
        <button
          type="button"
          onClick={() => revokeAll.mutate()}
          disabled={revokeAll.isPending}
          className="text-sm font-medium text-red-600 hover:underline disabled:opacity-60 dark:text-red-400"
        >
          {revokeAll.isPending ? 'Signing out everywhere…' : 'Sign out of all devices'}
        </button>
      )}
    </div>
  );
}
