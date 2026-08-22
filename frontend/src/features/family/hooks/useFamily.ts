import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  acceptInvitationRequest,
  cancelInvitationRequest,
  completeSharedTaskRequest,
  createEmergencyContactRequest,
  createFamilyRequest,
  declineInvitationRequest,
  deleteEmergencyContactRequest,
  getMyFamilyRequest,
  inviteMemberRequest,
  leaveFamilyRequest,
  listEmergencyContactsRequest,
  listFamilyInvitationsRequest,
  listMembersRequest,
  listMyInvitationsRequest,
  listSharedEventsRequest,
  listSharedNotesRequest,
  listSharedTasksRequest,
  removeMemberRequest,
  shareEventRequest,
  shareNoteRequest,
  shareTaskRequest,
  unshareEventRequest,
  unshareNoteRequest,
  unshareTaskRequest,
  updateEmergencyContactRequest,
  updateFamilyRequest,
  updateMemberRoleRequest,
  updateSharedTaskRequest,
} from '@/features/family/api';
import type { EmergencyContactPayload, FamilyRole } from '@/features/family/types';
import type { TaskPayload } from '@/features/tasks/types';

export const FAMILY_QUERY_KEY = ['family'] as const;
export const myFamilyQueryKey = [...FAMILY_QUERY_KEY, 'me'] as const;
export const familyMembersQueryKey = (familyId: string) =>
  [...FAMILY_QUERY_KEY, familyId, 'members'] as const;
export const familyInvitationsQueryKey = (familyId: string) =>
  [...FAMILY_QUERY_KEY, familyId, 'invitations'] as const;
export const myInvitationsQueryKey = [...FAMILY_QUERY_KEY, 'my-invitations'] as const;
export const emergencyContactsQueryKey = (familyId: string) =>
  [...FAMILY_QUERY_KEY, familyId, 'emergency-contacts'] as const;
export const sharedTasksQueryKey = (familyId: string) =>
  [...FAMILY_QUERY_KEY, familyId, 'shared-tasks'] as const;
export const sharedEventsQueryKey = (familyId: string) =>
  [...FAMILY_QUERY_KEY, familyId, 'shared-events'] as const;
export const sharedNotesQueryKey = (familyId: string) =>
  [...FAMILY_QUERY_KEY, familyId, 'shared-notes'] as const;

function useInvalidateFamily() {
  const queryClient = useQueryClient();
  return () => queryClient.invalidateQueries({ queryKey: FAMILY_QUERY_KEY });
}

// --------------------------------------------------------------------------
// Family & membership
// --------------------------------------------------------------------------

export function useMyFamily() {
  return useQuery({ queryKey: myFamilyQueryKey, queryFn: getMyFamilyRequest });
}

export function useCreateFamily() {
  const invalidateFamily = useInvalidateFamily();
  return useMutation({
    mutationFn: (name: string) => createFamilyRequest(name),
    onSuccess: invalidateFamily,
  });
}

export function useUpdateFamily(familyId: string) {
  const invalidateFamily = useInvalidateFamily();
  return useMutation({
    mutationFn: (name: string) => updateFamilyRequest(familyId, name),
    onSuccess: invalidateFamily,
  });
}

export function useLeaveFamily(familyId: string) {
  const invalidateFamily = useInvalidateFamily();
  return useMutation({
    mutationFn: () => leaveFamilyRequest(familyId),
    onSuccess: invalidateFamily,
  });
}

export function useFamilyMembers(familyId: string | undefined) {
  return useQuery({
    queryKey: familyMembersQueryKey(familyId ?? ''),
    queryFn: () => listMembersRequest(familyId as string),
    enabled: Boolean(familyId),
  });
}

export function useUpdateMemberRole(familyId: string) {
  const invalidateFamily = useInvalidateFamily();
  return useMutation({
    mutationFn: ({ membershipId, role }: { membershipId: string; role: FamilyRole }) =>
      updateMemberRoleRequest(familyId, membershipId, role),
    onSuccess: invalidateFamily,
  });
}

export function useRemoveMember(familyId: string) {
  const invalidateFamily = useInvalidateFamily();
  return useMutation({
    mutationFn: (membershipId: string) => removeMemberRequest(familyId, membershipId),
    onSuccess: invalidateFamily,
  });
}

// --------------------------------------------------------------------------
// Invitations
// --------------------------------------------------------------------------

export function useFamilyInvitations(familyId: string | undefined) {
  return useQuery({
    queryKey: familyInvitationsQueryKey(familyId ?? ''),
    queryFn: () => listFamilyInvitationsRequest(familyId as string),
    enabled: Boolean(familyId),
  });
}

export function useInviteMember(familyId: string) {
  const invalidateFamily = useInvalidateFamily();
  return useMutation({
    mutationFn: ({ email, role }: { email: string; role: Exclude<FamilyRole, 'owner'> }) =>
      inviteMemberRequest(familyId, email, role),
    onSuccess: invalidateFamily,
  });
}

export function useCancelInvitation(familyId: string) {
  const invalidateFamily = useInvalidateFamily();
  return useMutation({
    mutationFn: (invitationId: string) => cancelInvitationRequest(familyId, invitationId),
    onSuccess: invalidateFamily,
  });
}

export function useMyInvitations() {
  return useQuery({ queryKey: myInvitationsQueryKey, queryFn: listMyInvitationsRequest });
}

export function useAcceptInvitation() {
  const invalidateFamily = useInvalidateFamily();
  return useMutation({
    mutationFn: (token: string) => acceptInvitationRequest(token),
    onSuccess: invalidateFamily,
  });
}

export function useDeclineInvitation() {
  const invalidateFamily = useInvalidateFamily();
  return useMutation({
    mutationFn: (token: string) => declineInvitationRequest(token),
    onSuccess: invalidateFamily,
  });
}

// --------------------------------------------------------------------------
// Emergency contacts
// --------------------------------------------------------------------------

export function useEmergencyContacts(familyId: string | undefined) {
  return useQuery({
    queryKey: emergencyContactsQueryKey(familyId ?? ''),
    queryFn: () => listEmergencyContactsRequest(familyId as string),
    enabled: Boolean(familyId),
  });
}

export function useCreateEmergencyContact(familyId: string) {
  const invalidateFamily = useInvalidateFamily();
  return useMutation({
    mutationFn: (payload: EmergencyContactPayload) =>
      createEmergencyContactRequest(familyId, payload),
    onSuccess: invalidateFamily,
  });
}

export function useUpdateEmergencyContact(familyId: string) {
  const invalidateFamily = useInvalidateFamily();
  return useMutation({
    mutationFn: ({ contactId, payload }: { contactId: string; payload: EmergencyContactPayload }) =>
      updateEmergencyContactRequest(familyId, contactId, payload),
    onSuccess: invalidateFamily,
  });
}

export function useDeleteEmergencyContact(familyId: string) {
  const invalidateFamily = useInvalidateFamily();
  return useMutation({
    mutationFn: (contactId: string) => deleteEmergencyContactRequest(familyId, contactId),
    onSuccess: invalidateFamily,
  });
}

// --------------------------------------------------------------------------
// Shared resources
// --------------------------------------------------------------------------

export function useSharedTasks(familyId: string | undefined) {
  return useQuery({
    queryKey: sharedTasksQueryKey(familyId ?? ''),
    queryFn: () => listSharedTasksRequest(familyId as string),
    enabled: Boolean(familyId),
  });
}

export function useShareTask(familyId: string) {
  const invalidateFamily = useInvalidateFamily();
  return useMutation({
    mutationFn: ({ taskId, canEdit }: { taskId: string; canEdit: boolean }) =>
      shareTaskRequest(familyId, taskId, canEdit),
    onSuccess: invalidateFamily,
  });
}

export function useUnshareTask(familyId: string) {
  const invalidateFamily = useInvalidateFamily();
  return useMutation({
    mutationFn: (sharedId: string) => unshareTaskRequest(familyId, sharedId),
    onSuccess: invalidateFamily,
  });
}

export function useUpdateSharedTask(familyId: string) {
  const invalidateFamily = useInvalidateFamily();
  return useMutation({
    mutationFn: ({ sharedId, payload }: { sharedId: string; payload: TaskPayload }) =>
      updateSharedTaskRequest(familyId, sharedId, payload),
    onSuccess: invalidateFamily,
  });
}

export function useCompleteSharedTask(familyId: string) {
  const invalidateFamily = useInvalidateFamily();
  return useMutation({
    mutationFn: (sharedId: string) => completeSharedTaskRequest(familyId, sharedId),
    onSuccess: invalidateFamily,
  });
}

export function useSharedEvents(familyId: string | undefined) {
  return useQuery({
    queryKey: sharedEventsQueryKey(familyId ?? ''),
    queryFn: () => listSharedEventsRequest(familyId as string),
    enabled: Boolean(familyId),
  });
}

export function useShareEvent(familyId: string) {
  const invalidateFamily = useInvalidateFamily();
  return useMutation({
    mutationFn: (eventId: string) => shareEventRequest(familyId, eventId),
    onSuccess: invalidateFamily,
  });
}

export function useUnshareEvent(familyId: string) {
  const invalidateFamily = useInvalidateFamily();
  return useMutation({
    mutationFn: (sharedId: string) => unshareEventRequest(familyId, sharedId),
    onSuccess: invalidateFamily,
  });
}

export function useSharedNotes(familyId: string | undefined) {
  return useQuery({
    queryKey: sharedNotesQueryKey(familyId ?? ''),
    queryFn: () => listSharedNotesRequest(familyId as string),
    enabled: Boolean(familyId),
  });
}

export function useShareNote(familyId: string) {
  const invalidateFamily = useInvalidateFamily();
  return useMutation({
    mutationFn: (noteId: string) => shareNoteRequest(familyId, noteId),
    onSuccess: invalidateFamily,
  });
}

export function useUnshareNote(familyId: string) {
  const invalidateFamily = useInvalidateFamily();
  return useMutation({
    mutationFn: (sharedId: string) => unshareNoteRequest(familyId, sharedId),
    onSuccess: invalidateFamily,
  });
}
