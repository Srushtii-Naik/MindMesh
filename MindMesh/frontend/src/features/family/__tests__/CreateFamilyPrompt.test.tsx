import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, screen, waitFor } from '@testing-library/react';
import { renderWithProviders } from '@/test/renderWithProviders';
import { CreateFamilyPrompt } from '@/features/family/components/CreateFamilyPrompt';
import type { Family, FamilyInvitation } from '@/features/family/types';

const { createFamilyRequest, listMyInvitationsRequest, acceptInvitationRequest } = vi.hoisted(
  () => ({
    createFamilyRequest: vi.fn(),
    listMyInvitationsRequest: vi.fn(),
    acceptInvitationRequest: vi.fn(),
  })
);

vi.mock('@/features/family/api', async () => {
  const actual =
    await vi.importActual<typeof import('@/features/family/api')>('@/features/family/api');
  return {
    ...actual,
    createFamilyRequest,
    listMyInvitationsRequest,
    acceptInvitationRequest,
  };
});

function makeFamily(overrides: Partial<Family> = {}): Family {
  return {
    id: 'family-1',
    name: 'The Does',
    created_by: 'user-1',
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
    ...overrides,
  };
}

function makeInvitation(overrides: Partial<FamilyInvitation> = {}): FamilyInvitation {
  return {
    id: 'invite-1',
    family: makeFamily(),
    invited_email: 'me@example.com',
    role: 'adult',
    invited_by: { id: 'user-2', email: 'owner@example.com', full_name: 'Owner Person' },
    status: 'pending',
    expires_at: '2026-01-08T00:00:00Z',
    responded_at: null,
    created_at: '2026-01-01T00:00:00Z',
    ...overrides,
  };
}

beforeEach(() => {
  createFamilyRequest.mockReset();
  listMyInvitationsRequest.mockReset();
  acceptInvitationRequest.mockReset();
  listMyInvitationsRequest.mockResolvedValue([]);
});

describe('CreateFamilyPrompt', () => {
  it('creates a family on submit', async () => {
    createFamilyRequest.mockResolvedValue(makeFamily());

    renderWithProviders(<CreateFamilyPrompt />);

    fireEvent.change(screen.getByPlaceholderText(/the does/i), {
      target: { value: 'The Does' },
    });
    fireEvent.click(screen.getByRole('button', { name: /create family/i }));

    await waitFor(() => expect(createFamilyRequest).toHaveBeenCalledWith('The Does'));
  });

  it('shows a pending invitation and accepts it', async () => {
    listMyInvitationsRequest.mockResolvedValue([makeInvitation()]);
    acceptInvitationRequest.mockResolvedValue(makeFamily());

    renderWithProviders(<CreateFamilyPrompt />);

    expect(await screen.findByText('The Does')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /accept/i }));

    await waitFor(() => expect(acceptInvitationRequest).toHaveBeenCalledWith('invite-1'));
  });
});
