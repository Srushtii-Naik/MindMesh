/**
 * Family & Shared Workspace domain types (ROADMAP.md Milestone 10). Mirrors
 * the shape returned by apps/family/serializers.py.
 */
import type { CalendarEvent } from '@/features/calendar/types';
import type { Note } from '@/features/notes/types';
import type { Task } from '@/features/tasks/types';

export type FamilyRole = 'owner' | 'adult' | 'child';

export type InvitationStatus = 'pending' | 'accepted' | 'declined' | 'canceled' | 'expired';

export interface Family {
  id: string;
  name: string;
  created_by: string | null;
  created_at: string;
  updated_at: string;
}

export interface MemberUser {
  id: string;
  email: string;
  full_name: string;
}

export interface FamilyMembership {
  id: string;
  user: MemberUser;
  role: FamilyRole;
  created_at: string;
}

export interface FamilyInvitation {
  id: string;
  family: Family;
  invited_email: string;
  role: FamilyRole;
  invited_by: MemberUser;
  status: InvitationStatus;
  expires_at: string;
  responded_at: string | null;
  created_at: string;
}

export interface EmergencyContact {
  id: string;
  name: string;
  relationship: string;
  phone_number: string;
  email: string;
  notes: string;
  added_by: string | null;
  created_at: string;
  updated_at: string;
}

export interface EmergencyContactPayload {
  name?: string;
  relationship?: string;
  phone_number?: string;
  email?: string;
  notes?: string;
}

export type SharedResourceType = 'task' | 'event' | 'note';

export interface SharedResourceMeta {
  id: string;
  resource_type: SharedResourceType;
  owner: MemberUser;
  shared_by: MemberUser;
  can_edit: boolean;
  created_at: string;
}

export interface SharedTask {
  share: SharedResourceMeta;
  task: Task;
}

export interface SharedEvent {
  share: SharedResourceMeta;
  event: CalendarEvent;
}

export interface SharedNote {
  share: SharedResourceMeta;
  note: Note;
}
