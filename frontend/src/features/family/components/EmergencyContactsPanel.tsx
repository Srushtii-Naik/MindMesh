import { useState } from 'react';
import { useAuthStore } from '@/features/auth';
import {
  useCreateEmergencyContact,
  useDeleteEmergencyContact,
  useEmergencyContacts,
  useFamilyMembers,
} from '@/features/family/hooks';
import type { Family } from '@/features/family/types';
import { extractApiErrorMessage } from '@/api/errors';

/**
 * Emergency contacts, visible to every family member but only manageable by
 * owner/adult members (ROADMAP.md Milestone 10: "Emergency contacts
 * implemented and accessible appropriately").
 */
export function EmergencyContactsPanel({ family }: { family: Family }) {
  const currentUserId = useAuthStore((state) => state.user?.id);
  const { data: members } = useFamilyMembers(family.id);
  const myMembership = members?.find((m) => m.user.id === currentUserId);
  const canManage = myMembership?.role === 'owner' || myMembership?.role === 'adult';

  const { data: contacts, isLoading } = useEmergencyContacts(family.id);
  const createContact = useCreateEmergencyContact(family.id);
  const deleteContact = useDeleteEmergencyContact(family.id);

  const [name, setName] = useState('');
  const [relationship, setRelationship] = useState('');
  const [phoneNumber, setPhoneNumber] = useState('');
  const [error, setError] = useState<string | null>(null);

  function handleCreate(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    createContact.mutate(
      { name, relationship, phone_number: phoneNumber },
      {
        onSuccess: () => {
          setName('');
          setRelationship('');
          setPhoneNumber('');
        },
        onError: (err) => setError(extractApiErrorMessage(err)),
      }
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="mb-3 text-sm font-medium text-slate-700 dark:text-slate-300">
          Emergency contacts
        </h2>
        {isLoading && <p className="text-sm text-slate-500 dark:text-slate-400">Loading…</p>}
        {!isLoading && contacts?.length === 0 && (
          <p className="text-sm text-slate-500 dark:text-slate-400">No emergency contacts yet.</p>
        )}
        <ul className="flex flex-col gap-2">
          {contacts?.map((contact) => (
            <li
              key={contact.id}
              className="flex items-start justify-between gap-3 rounded-lg border border-slate-200 bg-white p-3 dark:border-slate-700 dark:bg-slate-800"
            >
              <div className="min-w-0">
                <p className="truncate text-sm font-medium text-slate-900 dark:text-slate-100">
                  {contact.name}
                  {contact.relationship && (
                    <span className="ml-1 text-xs text-slate-400">({contact.relationship})</span>
                  )}
                </p>
                <p className="text-sm text-slate-600 dark:text-slate-300">{contact.phone_number}</p>
                {contact.email && (
                  <p className="text-xs text-slate-500 dark:text-slate-400">{contact.email}</p>
                )}
              </div>
              {canManage && (
                <button
                  type="button"
                  onClick={() => deleteContact.mutate(contact.id)}
                  className="shrink-0 text-xs font-medium text-slate-500 hover:text-red-600 dark:text-slate-400 dark:hover:text-red-400"
                >
                  Remove
                </button>
              )}
            </li>
          ))}
        </ul>
      </div>

      {canManage && (
        <form onSubmit={handleCreate} className="flex flex-col gap-3">
          <h2 className="text-sm font-medium text-slate-700 dark:text-slate-300">Add a contact</h2>
          <div className="grid grid-cols-1 gap-2 sm:grid-cols-3">
            <input
              type="text"
              value={name}
              onChange={(event) => setName(event.target.value)}
              placeholder="Name"
              className="rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
            />
            <input
              type="text"
              value={relationship}
              onChange={(event) => setRelationship(event.target.value)}
              placeholder="Relationship (optional)"
              className="rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
            />
            <input
              type="text"
              value={phoneNumber}
              onChange={(event) => setPhoneNumber(event.target.value)}
              placeholder="Phone number"
              className="rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
            />
          </div>
          {error && <p className="text-sm text-red-600 dark:text-red-400">{error}</p>}
          <button
            type="submit"
            disabled={createContact.isPending || !name.trim() || !phoneNumber.trim()}
            className="self-start rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-brand-700 disabled:opacity-60"
          >
            {createContact.isPending ? 'Adding…' : 'Add contact'}
          </button>
        </form>
      )}
    </div>
  );
}
