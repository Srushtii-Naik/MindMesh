import { useState } from 'react';
import { useAuthStore } from '@/features/auth';
import {
  useCancelInvitation,
  useFamilyInvitations,
  useFamilyMembers,
  useInviteMember,
  useRemoveMember,
  useUpdateMemberRole,
} from '@/features/family/hooks';
import type { Family, FamilyRole } from '@/features/family/types';
import { extractApiErrorMessage } from '@/api/errors';

const ROLE_LABELS: Record<FamilyRole, string> = {
  owner: 'Owner',
  adult: 'Adult',
  child: 'Child',
};

/**
 * Member roster + invitations (ROADMAP.md Milestone 10: "Family members
 * (invite/manage)"). Owner/adult-only actions (invite, change role, remove)
 * are hidden for a CHILD-role viewer — the backend enforces the same rule,
 * this just avoids showing controls that would 403.
 */
export function FamilyMembersPanel({ family }: { family: Family }) {
  const currentUserId = useAuthStore((state) => state.user?.id);

  const { data: members, isLoading: membersLoading } = useFamilyMembers(family.id);
  const { data: invitations } = useFamilyInvitations(family.id);
  const inviteMember = useInviteMember(family.id);
  const cancelInvitation = useCancelInvitation(family.id);
  const updateRole = useUpdateMemberRole(family.id);
  const removeMember = useRemoveMember(family.id);

  const myMembership = members?.find((m) => m.user.id === currentUserId);
  const canManage = myMembership?.role === 'owner' || myMembership?.role === 'adult';
  const isOwner = myMembership?.role === 'owner';

  const [email, setEmail] = useState('');
  const [role, setRole] = useState<Exclude<FamilyRole, 'owner'>>('adult');
  const [inviteError, setInviteError] = useState<string | null>(null);

  function handleInvite(event: React.FormEvent) {
    event.preventDefault();
    setInviteError(null);
    inviteMember.mutate(
      { email, role },
      {
        onSuccess: () => setEmail(''),
        onError: (err) => setInviteError(extractApiErrorMessage(err)),
      }
    );
  }

  const pendingInvitations = (invitations ?? []).filter((i) => i.status === 'pending');

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="mb-3 text-sm font-medium text-slate-700 dark:text-slate-300">Members</h2>
        {membersLoading && <p className="text-sm text-slate-500 dark:text-slate-400">Loading…</p>}
        <ul className="flex flex-col gap-2">
          {members?.map((member) => (
            <li
              key={member.id}
              className="flex items-center justify-between gap-3 rounded-lg border border-slate-200 bg-white p-3 dark:border-slate-700 dark:bg-slate-800"
            >
              <div className="min-w-0">
                <p className="truncate text-sm font-medium text-slate-900 dark:text-slate-100">
                  {member.user.full_name}
                  {member.user.id === currentUserId && (
                    <span className="ml-1 text-xs text-slate-400">(you)</span>
                  )}
                </p>
                <p className="truncate text-xs text-slate-500 dark:text-slate-400">
                  {member.user.email}
                </p>
              </div>

              <div className="flex shrink-0 items-center gap-2">
                {isOwner ? (
                  <select
                    value={member.role}
                    onChange={(event) =>
                      updateRole.mutate({
                        membershipId: member.id,
                        role: event.target.value as FamilyRole,
                      })
                    }
                    className="rounded-md border border-slate-300 bg-white px-2 py-1 text-xs dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
                  >
                    {(['owner', 'adult', 'child'] as FamilyRole[]).map((r) => (
                      <option key={r} value={r}>
                        {ROLE_LABELS[r]}
                      </option>
                    ))}
                  </select>
                ) : (
                  <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-600 dark:bg-slate-700 dark:text-slate-300">
                    {ROLE_LABELS[member.role]}
                  </span>
                )}

                {isOwner && member.user.id !== currentUserId && (
                  <button
                    type="button"
                    onClick={() => removeMember.mutate(member.id)}
                    className="text-xs font-medium text-slate-500 hover:text-red-600 dark:text-slate-400 dark:hover:text-red-400"
                  >
                    Remove
                  </button>
                )}
              </div>
            </li>
          ))}
        </ul>
      </div>

      {canManage && pendingInvitations.length > 0 && (
        <div>
          <h2 className="mb-3 text-sm font-medium text-slate-700 dark:text-slate-300">
            Pending invitations sent
          </h2>
          <ul className="flex flex-col gap-2">
            {pendingInvitations.map((invitation) => (
              <li
                key={invitation.id}
                className="flex items-center justify-between gap-3 rounded-lg border border-slate-200 bg-white p-3 dark:border-slate-700 dark:bg-slate-800"
              >
                <div className="min-w-0">
                  <p className="truncate text-sm text-slate-900 dark:text-slate-100">
                    {invitation.invited_email}
                  </p>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    Invited as {ROLE_LABELS[invitation.role]}
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => cancelInvitation.mutate(invitation.id)}
                  className="shrink-0 text-xs font-medium text-slate-500 hover:text-red-600 dark:text-slate-400 dark:hover:text-red-400"
                >
                  Cancel
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}

      {canManage && (
        <form onSubmit={handleInvite} className="flex flex-col gap-3">
          <h2 className="text-sm font-medium text-slate-700 dark:text-slate-300">Invite someone</h2>
          <div className="flex flex-col gap-2 sm:flex-row">
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="email@example.com"
              className="flex-1 rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
            />
            <select
              value={role}
              onChange={(event) => setRole(event.target.value as Exclude<FamilyRole, 'owner'>)}
              className="rounded-md border border-slate-300 bg-white px-2 py-2 text-sm dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
            >
              <option value="adult">Adult</option>
              <option value="child">Child</option>
            </select>
            <button
              type="submit"
              disabled={inviteMember.isPending || !email.trim()}
              className="rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-brand-700 disabled:opacity-60"
            >
              {inviteMember.isPending ? 'Sending…' : 'Invite'}
            </button>
          </div>
          {inviteError && <p className="text-sm text-red-600 dark:text-red-400">{inviteError}</p>}
        </form>
      )}
    </div>
  );
}
