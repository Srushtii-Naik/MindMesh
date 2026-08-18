import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, fireEvent, waitFor } from '@testing-library/react';
import { renderWithProviders } from '@/test/renderWithProviders';
import { NotificationList } from '@/features/notifications/components/NotificationList';
import type { Notification } from '@/features/notifications/types';

const { listNotificationsRequest, deleteNotificationRequest, updateNotificationReadStateRequest } =
  vi.hoisted(() => ({
    listNotificationsRequest: vi.fn(),
    deleteNotificationRequest: vi.fn(),
    updateNotificationReadStateRequest: vi.fn(),
  }));

vi.mock('@/features/notifications/api', async () => {
  const actual = await vi.importActual<typeof import('@/features/notifications/api')>(
    '@/features/notifications/api'
  );
  return {
    ...actual,
    listNotificationsRequest,
    deleteNotificationRequest,
    updateNotificationReadStateRequest,
  };
});

function makeNotification(overrides: Partial<Notification> = {}): Notification {
  return {
    id: 'notif-1',
    notification_type: 'reminder',
    title: 'Take medication',
    message: 'Take your evening medication.',
    reminder: null,
    is_read: false,
    read_at: null,
    deliveries: [],
    created_at: '2026-01-01T09:00:00Z',
    updated_at: '2026-01-01T09:00:00Z',
    ...overrides,
  };
}

beforeEach(() => {
  listNotificationsRequest.mockReset();
  deleteNotificationRequest.mockReset();
  updateNotificationReadStateRequest.mockReset();
});

describe('NotificationList', () => {
  it('shows an empty state when there are no notifications', async () => {
    listNotificationsRequest.mockResolvedValue({
      count: 0,
      next: null,
      previous: null,
      results: [],
    });

    renderWithProviders(<NotificationList />);

    await waitFor(() => expect(screen.getByText('No notifications yet.')).toBeInTheDocument());
  });

  it('renders each notification with its message', async () => {
    listNotificationsRequest.mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [makeNotification()],
    });

    renderWithProviders(<NotificationList />);

    expect(await screen.findByText('Take medication')).toBeInTheDocument();
    expect(screen.getByText('Take your evening medication.')).toBeInTheDocument();
  });

  it('shows an error state when the request fails', async () => {
    listNotificationsRequest.mockRejectedValue(new Error('network error'));

    renderWithProviders(<NotificationList />);

    await waitFor(() =>
      expect(screen.getByText("Couldn't load notifications.")).toBeInTheDocument()
    );
  });

  it('dismisses a notification', async () => {
    listNotificationsRequest.mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [makeNotification()],
    });
    deleteNotificationRequest.mockResolvedValue(undefined);

    renderWithProviders(<NotificationList />);

    const dismissButton = await screen.findByRole('button', { name: /dismiss/i });
    fireEvent.click(dismissButton);

    await waitFor(() => expect(deleteNotificationRequest).toHaveBeenCalledWith('notif-1'));
  });

  it('marks a notification read', async () => {
    listNotificationsRequest.mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [makeNotification()],
    });
    updateNotificationReadStateRequest.mockResolvedValue(makeNotification({ is_read: true }));

    renderWithProviders(<NotificationList />);

    const markReadButton = await screen.findByRole('button', { name: /mark read/i });
    fireEvent.click(markReadButton);

    await waitFor(() =>
      expect(updateNotificationReadStateRequest).toHaveBeenCalledWith('notif-1', true)
    );
  });

  it('refetches with is_read=false when Unread only is toggled', async () => {
    listNotificationsRequest.mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [makeNotification()],
    });

    renderWithProviders(<NotificationList />);
    await screen.findByText('Take medication');

    fireEvent.click(screen.getByLabelText(/unread only/i));

    await waitFor(() =>
      expect(listNotificationsRequest).toHaveBeenLastCalledWith({ is_read: false })
    );
  });
});
