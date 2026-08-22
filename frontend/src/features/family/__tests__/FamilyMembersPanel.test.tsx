import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, screen, waitFor } from '@testing-library/react';
import { renderWithProviders } from '@/test/renderWithProviders';
import { useAuthStore } from '@/features/auth';
import { FamilyMembersPanel } from '@/features/family/components/FamilyMembersPanel';
import type { Family, FamilyMembership } from '@/features/family/types';

const {
  listMembersRequest,
  listFamilyInvitationsRequest,
  inviteMemberRequest,
  removeMemberRequest,
} = vi.hoisted(() => ({
  listMembersRequest: vi.fn(),
  listFamilyInvitationsRequest: vi.fn(),
  inviteMemberRequest: vi.fn(),
  removeMemberRequest: vi.fn(),
}));

vi.mock('@/features/family/api', async () => {
  const actual =
    await vi.importActual<typeof import('@/features/family/api')>('@/features/family/api');
  return {
    ...actual,
    listMembersRequest,
    listFamilyInvitationsRequest,
    inviteMemberRequest,
    removeMemberRequest,
  };
});

const family: Family = {
  id: 'family-1',
  name: 'The Does',
  created_by: 'user-1',
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
};

function makeMembership(overrides: Partial<FamilyMembership> = {}): FamilyMembership {
  return {
    id: 'member-1',
    user: { id: 'user-1', email: 'owner@example.com', full_name: 'Owner Person' },
    role: 'owner',
    created_at: '2026-01-01T00:00:00Z',
    ...overrides,
  };
}

beforeEach(() => {
  listMembersRequest.mockReset();
  listFamilyInvitationsRequest.mockReset();
  inviteMemberRequest.mockReset();
  removeMemberRequest.mockReset();
  listFamilyInvitationsRequest.mockResolvedValue([]);
  useAuthStore.setState({
    user: { id: 'user-1', email: 'owner@example.com', full_name: 'Owner Person', created_at: '' },
    isAuthenticated: true,
  });
});

describe('FamilyMembersPanel', () => {
  it('lists members and lets the owner invite someone', async () => {
    listMembersRequest.mockResolvedValue([makeMembership()]);
    inviteMemberRequest.mockResolvedValue({});

    renderWithProviders(<FamilyMembersPanel family={family} />);

    expect(await screen.findByText('Owner Person')).toBeInTheDocument();
    expect(await screen.findByText(/invite someone/i)).toBeInTheDocument();

    fireEvent.change(screen.getByPlaceholderText('email@example.com'), {
      target: { value: 'kid@example.com' },
    });
    fireEvent.click(screen.getByRole('button', { name: /^invite$/i }));

    await waitFor(() =>
      expect(inviteMemberRequest).toHaveBeenCalledWith('family-1', 'kid@example.com', 'adult')
    );
  });

  it('lets the owner remove another member but not themselves', async () => {
    listMembersRequest.mockResolvedValue([
      makeMembership(),
      makeMembership({
        id: 'member-2',
        role: 'adult',
        user: { id: 'user-2', email: 'kid@example.com', full_name: 'Kid Person' },
      }),
    ]);

    renderWithProviders(<FamilyMembersPanel family={family} />);

    await screen.findByText('Kid Person');
    const removeButtons = screen.getAllByRole('button', { name: /remove/i });
    expect(removeButtons).toHaveLength(1);

    fireEvent.click(removeButtons[0]);
    await waitFor(() => expect(removeMemberRequest).toHaveBeenCalledWith('family-1', 'member-2'));
  });

  it('hides invite/remove controls for a child-role viewer', async () => {
    listMembersRequest.mockResolvedValue([
      makeMembership({
        id: 'member-3',
        role: 'child',
        user: { id: 'user-1', email: 'owner@example.com', full_name: 'Owner Person' },
      }),
    ]);

    renderWithProviders(<FamilyMembersPanel family={family} />);

    await screen.findByText('Owner Person');
    expect(screen.queryByText(/invite someone/i)).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /remove/i })).not.toBeInTheDocument();
  });
});
