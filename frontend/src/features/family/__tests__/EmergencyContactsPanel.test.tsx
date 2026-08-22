import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, screen, waitFor } from '@testing-library/react';
import { renderWithProviders } from '@/test/renderWithProviders';
import { useAuthStore } from '@/features/auth';
import { EmergencyContactsPanel } from '@/features/family/components/EmergencyContactsPanel';
import type { EmergencyContact, Family, FamilyMembership } from '@/features/family/types';

const { listMembersRequest, listEmergencyContactsRequest, createEmergencyContactRequest } =
  vi.hoisted(() => ({
    listMembersRequest: vi.fn(),
    listEmergencyContactsRequest: vi.fn(),
    createEmergencyContactRequest: vi.fn(),
  }));

vi.mock('@/features/family/api', async () => {
  const actual =
    await vi.importActual<typeof import('@/features/family/api')>('@/features/family/api');
  return {
    ...actual,
    listMembersRequest,
    listEmergencyContactsRequest,
    createEmergencyContactRequest,
  };
});

const family: Family = {
  id: 'family-1',
  name: 'The Does',
  created_by: 'user-1',
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
};

function makeContact(overrides: Partial<EmergencyContact> = {}): EmergencyContact {
  return {
    id: 'contact-1',
    name: 'Dr. Smith',
    relationship: 'Family doctor',
    phone_number: '555-0100',
    email: '',
    notes: '',
    added_by: 'user-1',
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
    ...overrides,
  };
}

function makeMembership(role: FamilyMembership['role']): FamilyMembership {
  return {
    id: 'member-1',
    user: { id: 'user-1', email: 'owner@example.com', full_name: 'Owner Person' },
    role,
    created_at: '2026-01-01T00:00:00Z',
  };
}

beforeEach(() => {
  listMembersRequest.mockReset();
  listEmergencyContactsRequest.mockReset();
  createEmergencyContactRequest.mockReset();
  useAuthStore.setState({
    user: { id: 'user-1', email: 'owner@example.com', full_name: 'Owner Person', created_at: '' },
    isAuthenticated: true,
  });
});

describe('EmergencyContactsPanel', () => {
  it('lists contacts and lets an owner add one', async () => {
    listMembersRequest.mockResolvedValue([makeMembership('owner')]);
    listEmergencyContactsRequest.mockResolvedValue([makeContact()]);
    createEmergencyContactRequest.mockResolvedValue(makeContact({ id: 'contact-2' }));

    renderWithProviders(<EmergencyContactsPanel family={family} />);

    expect(await screen.findByText('Dr. Smith')).toBeInTheDocument();

    fireEvent.change(screen.getByPlaceholderText('Name'), { target: { value: 'Grandma' } });
    fireEvent.change(screen.getByPlaceholderText('Phone number'), {
      target: { value: '555-0200' },
    });
    fireEvent.click(screen.getByRole('button', { name: /add contact/i }));

    await waitFor(() =>
      expect(createEmergencyContactRequest).toHaveBeenCalledWith('family-1', {
        name: 'Grandma',
        relationship: '',
        phone_number: '555-0200',
      })
    );
  });

  it('hides the add form for a child-role viewer', async () => {
    listMembersRequest.mockResolvedValue([makeMembership('child')]);
    listEmergencyContactsRequest.mockResolvedValue([makeContact()]);

    renderWithProviders(<EmergencyContactsPanel family={family} />);

    await screen.findByText('Dr. Smith');
    expect(screen.queryByRole('button', { name: /add contact/i })).not.toBeInTheDocument();
  });
});
