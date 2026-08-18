import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, fireEvent, waitFor } from '@testing-library/react';
import { renderWithProviders } from '@/test/renderWithProviders';
import { NotificationBell } from '@/features/notifications/components/NotificationBell';
import type { Notification } from '@/features/notifications/types';

const {
  listNotificationsRequest,
  getUnreadCountRequest,
  markAllNotificationsReadRequest,
  updateNotificationReadStateRequest,
} = vi.hoisted(() => ({
  listNotificationsRequest: vi.fn(),
  getUnreadCountRequest: vi.fn(),
  markAllNotificationsReadRequest: vi.fn(),
  updateNotificationReadStateRequest: vi.fn(),
}));

vi.mock('@/features/notifications/api', async () => {
  const actual = await vi.importActual<typeof import('@/features/notifications/api')>(
    '@/features/notifications/api'
  );
  return {
    ...actual,
    listNotificationsRequest,
    getUnreadCountRequest,
    markAllNotificationsReadRequest,
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
  getUnreadCountRequest.mockReset();
  markAllNotificationsReadRequest.mockReset();
  updateNotificationReadStateRequest.mockReset();
  listNotificationsRequest.mockResolvedValue({ count: 0, next: null, previous: null, results: [] });
  getUnreadCountRequest.mockResolvedValue(0);
});

describe('NotificationBell', () => {
  it('shows no badge when there are no unread notifications', async () => {
    renderWithProviders(<NotificationBell />);

    await waitFor(() => expect(getUnreadCountRequest).toHaveBeenCalled());
    expect(screen.queryByTestId('notification-badge')).not.toBeInTheDocument();
  });

  it('shows the unread count badge', async () => {
    getUnreadCountRequest.mockResolvedValue(3);

    renderWithProviders(<NotificationBell />);

    await waitFor(() => expect(screen.getByTestId('notification-badge')).toHaveTextContent('3'));
  });

  it('caps the badge at 9+', async () => {
    getUnreadCountRequest.mockResolvedValue(15);

    renderWithProviders(<NotificationBell />);

    await waitFor(() => expect(screen.getByTestId('notification-badge')).toHaveTextContent('9+'));
  });

  it('opens the dropdown and lists notifications on click', async () => {
    getUnreadCountRequest.mockResolvedValue(1);
    listNotificationsRequest.mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [makeNotification()],
    });

    renderWithProviders(<NotificationBell />);

    fireEvent.click(screen.getByRole('button', { name: /notifications/i }));

    expect(await screen.findByText('Take medication')).toBeInTheDocument();
  });

  it('shows an empty state when there are no notifications', async () => {
    renderWithProviders(<NotificationBell />);

    fireEvent.click(screen.getByRole('button', { name: /notifications/i }));

    expect(await screen.findByText(/all caught up/i)).toBeInTheDocument();
  });

  it('marks an unread notification read on click', async () => {
    getUnreadCountRequest.mockResolvedValue(1);
    listNotificationsRequest.mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [makeNotification()],
    });
    updateNotificationReadStateRequest.mockResolvedValue(makeNotification({ is_read: true }));

    renderWithProviders(<NotificationBell />);
    fireEvent.click(screen.getByRole('button', { name: /notifications/i }));

    const item = await screen.findByText('Take medication');
    fireEvent.click(item);

    await waitFor(() =>
      expect(updateNotificationReadStateRequest).toHaveBeenCalledWith('notif-1', true)
    );
  });

  it('calls mark-all-read when the button is clicked', async () => {
    getUnreadCountRequest.mockResolvedValue(2);
    listNotificationsRequest.mockResolvedValue({
      count: 2,
      next: null,
      previous: null,
      results: [makeNotification({ id: 'a' }), makeNotification({ id: 'b' })],
    });
    markAllNotificationsReadRequest.mockResolvedValue({ updated: 2 });

    renderWithProviders(<NotificationBell />);
    fireEvent.click(screen.getByRole('button', { name: /notifications/i }));

    const markAllButton = await screen.findByRole('button', { name: /mark all read/i });
    fireEvent.click(markAllButton);

    await waitFor(() => expect(markAllNotificationsReadRequest).toHaveBeenCalled());
  });
});
