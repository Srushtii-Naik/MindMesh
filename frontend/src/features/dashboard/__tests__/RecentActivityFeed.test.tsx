import { describe, it, expect, vi } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import { renderWithProviders } from '@/test/renderWithProviders';
import { RecentActivityFeed } from '@/features/dashboard/components/RecentActivityFeed';

const { getProfileRequest, getSettingsRequest, listSessionsRequest } = vi.hoisted(() => ({
  getProfileRequest: vi.fn(),
  getSettingsRequest: vi.fn(),
  listSessionsRequest: vi.fn(),
}));

vi.mock('@/features/auth/api', () => ({
  getProfileRequest,
  getSettingsRequest,
  listSessionsRequest,
}));

describe('RecentActivityFeed', () => {
  it('renders activity derived from real profile/settings/session data', async () => {
    getProfileRequest.mockResolvedValue({
      id: 'user-1',
      email: 'jane@example.com',
      full_name: 'Jane Doe',
      created_at: '2026-01-01T09:00:00Z',
      auth_provider: 'email',
      updated_at: '2026-01-01T09:00:00Z',
    });
    getSettingsRequest.mockResolvedValue({
      theme_preference: 'system',
      email_notifications_enabled: true,
      updated_at: '2026-01-01T09:00:00Z',
    });
    listSessionsRequest.mockResolvedValue([
      { id: 1, created_at: '2026-01-02T08:00:00Z', expires_at: '2026-01-09T08:00:00Z' },
    ]);

    renderWithProviders(<RecentActivityFeed />);

    expect(await screen.findByText('Account created')).toBeInTheDocument();
    expect(screen.getByText('Signed in')).toBeInTheDocument();
  });

  it('shows an empty state when there is no data', async () => {
    getProfileRequest.mockResolvedValue(null as never);
    getSettingsRequest.mockResolvedValue(null as never);
    listSessionsRequest.mockResolvedValue([]);

    renderWithProviders(<RecentActivityFeed />);

    await waitFor(() => expect(screen.getByText('No activity yet.')).toBeInTheDocument());
  });
});
