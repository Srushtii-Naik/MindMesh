import { apiClient } from '@/api/client';
import type {
  EmergencyContact,
  EmergencyContactPayload,
  Family,
  FamilyInvitation,
  FamilyMembership,
  FamilyRole,
  SharedEvent,
  SharedNote,
  SharedTask,
} from '@/features/family/types';
import type { TaskPayload } from '@/features/tasks/types';

/**
 * Family & Shared Workspace domain requests (ROADMAP.md Milestone 10).
 * Consumed exclusively via the TanStack Query hooks in
 * `features/family/hooks/`, per ARCHITECTURE.md Section 2.
 */

// --------------------------------------------------------------------------
// Family & membership
// --------------------------------------------------------------------------

export async function getMyFamilyRequest(): Promise<Family | null> {
  try {
    const { data } = await apiClient.get<Family>('/family/me/');
    return data;
  } catch (error) {
    const status = (error as { response?: { status?: number } }).response?.status;
    if (status === 404) {
      return null;
    }
    throw error;
  }
}

export async function createFamilyRequest(name: string): Promise<Family> {
  const { data } = await apiClient.post<Family>('/family/', { name });
  return data;
}

export async function updateFamilyRequest(familyId: string, name: string): Promise<Family> {
  const { data } = await apiClient.patch<Family>(`/family/${familyId}/`, { name });
  return data;
}

export async function leaveFamilyRequest(familyId: string): Promise<void> {
  await apiClient.post(`/family/${familyId}/leave/`);
}

export async function listMembersRequest(familyId: string): Promise<FamilyMembership[]> {
  const { data } = await apiClient.get<FamilyMembership[]>(`/family/${familyId}/members/`);
  return data;
}

export async function updateMemberRoleRequest(
  familyId: string,
  membershipId: string,
  role: FamilyRole
): Promise<FamilyMembership> {
  const { data } = await apiClient.patch<FamilyMembership>(
    `/family/${familyId}/members/${membershipId}/`,
    { role }
  );
  return data;
}

export async function removeMemberRequest(familyId: string, membershipId: string): Promise<void> {
  await apiClient.delete(`/family/${familyId}/members/${membershipId}/`);
}

// --------------------------------------------------------------------------
// Invitations
// --------------------------------------------------------------------------

export async function listFamilyInvitationsRequest(familyId: string): Promise<FamilyInvitation[]> {
  const { data } = await apiClient.get<FamilyInvitation[]>(`/family/${familyId}/invitations/`);
  return data;
}

export async function inviteMemberRequest(
  familyId: string,
  email: string,
  role: Exclude<FamilyRole, 'owner'>
): Promise<FamilyInvitation> {
  const { data } = await apiClient.post<FamilyInvitation>(`/family/${familyId}/invitations/`, {
    email,
    role,
  });
  return data;
}

export async function cancelInvitationRequest(
  familyId: string,
  invitationId: string
): Promise<void> {
  await apiClient.delete(`/family/${familyId}/invitations/${invitationId}/`);
}

export async function listMyInvitationsRequest(): Promise<FamilyInvitation[]> {
  const { data } = await apiClient.get<FamilyInvitation[]>('/family/invitations/');
  return data;
}

export async function acceptInvitationRequest(token: string): Promise<Family> {
  const { data } = await apiClient.post<Family>(`/family/invitations/${token}/accept/`);
  return data;
}

export async function declineInvitationRequest(token: string): Promise<FamilyInvitation> {
  const { data } = await apiClient.post<FamilyInvitation>(`/family/invitations/${token}/decline/`);
  return data;
}

// --------------------------------------------------------------------------
// Emergency contacts
// --------------------------------------------------------------------------

export async function listEmergencyContactsRequest(familyId: string): Promise<EmergencyContact[]> {
  const { data } = await apiClient.get<EmergencyContact[]>(
    `/family/${familyId}/emergency-contacts/`
  );
  return data;
}

export async function createEmergencyContactRequest(
  familyId: string,
  payload: EmergencyContactPayload
): Promise<EmergencyContact> {
  const { data } = await apiClient.post<EmergencyContact>(
    `/family/${familyId}/emergency-contacts/`,
    payload
  );
  return data;
}

export async function updateEmergencyContactRequest(
  familyId: string,
  contactId: string,
  payload: EmergencyContactPayload
): Promise<EmergencyContact> {
  const { data } = await apiClient.patch<EmergencyContact>(
    `/family/${familyId}/emergency-contacts/${contactId}/`,
    payload
  );
  return data;
}

export async function deleteEmergencyContactRequest(
  familyId: string,
  contactId: string
): Promise<void> {
  await apiClient.delete(`/family/${familyId}/emergency-contacts/${contactId}/`);
}

// --------------------------------------------------------------------------
// Shared resources
// --------------------------------------------------------------------------

export async function listSharedTasksRequest(familyId: string): Promise<SharedTask[]> {
  const { data } = await apiClient.get<SharedTask[]>(`/family/${familyId}/shared-tasks/`);
  return data;
}

export async function shareTaskRequest(
  familyId: string,
  resourceId: string,
  canEdit: boolean
): Promise<void> {
  await apiClient.post(`/family/${familyId}/shared-tasks/`, {
    resource_id: resourceId,
    can_edit: canEdit,
  });
}

export async function unshareTaskRequest(familyId: string, sharedId: string): Promise<void> {
  await apiClient.delete(`/family/${familyId}/shared-tasks/${sharedId}/`);
}

export async function updateSharedTaskRequest(
  familyId: string,
  sharedId: string,
  payload: TaskPayload
): Promise<void> {
  await apiClient.patch(`/family/${familyId}/shared-tasks/${sharedId}/task/`, payload);
}

export async function completeSharedTaskRequest(familyId: string, sharedId: string): Promise<void> {
  await apiClient.post(`/family/${familyId}/shared-tasks/${sharedId}/complete/`);
}

export async function listSharedEventsRequest(familyId: string): Promise<SharedEvent[]> {
  const { data } = await apiClient.get<SharedEvent[]>(`/family/${familyId}/shared-events/`);
  return data;
}

export async function shareEventRequest(familyId: string, resourceId: string): Promise<void> {
  await apiClient.post(`/family/${familyId}/shared-events/`, { resource_id: resourceId });
}

export async function unshareEventRequest(familyId: string, sharedId: string): Promise<void> {
  await apiClient.delete(`/family/${familyId}/shared-events/${sharedId}/`);
}

export async function listSharedNotesRequest(familyId: string): Promise<SharedNote[]> {
  const { data } = await apiClient.get<SharedNote[]>(`/family/${familyId}/shared-notes/`);
  return data;
}

export async function shareNoteRequest(familyId: string, resourceId: string): Promise<void> {
  await apiClient.post(`/family/${familyId}/shared-notes/`, { resource_id: resourceId });
}

export async function unshareNoteRequest(familyId: string, sharedId: string): Promise<void> {
  await apiClient.delete(`/family/${familyId}/shared-notes/${sharedId}/`);
}
