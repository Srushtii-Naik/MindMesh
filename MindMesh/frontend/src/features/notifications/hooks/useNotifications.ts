import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  deleteNotificationRequest,
  getUnreadCountRequest,
  listNotificationsRequest,
  markAllNotificationsReadRequest,
  registerDeviceTokenRequest,
  unregisterDeviceTokenRequest,
  updateNotificationReadStateRequest,
} from '@/features/notifications/api';
import type { DeviceTokenPayload, NotificationFilters } from '@/features/notifications/types';

export const NOTIFICATIONS_QUERY_KEY = ['notifications'] as const;
export const notificationListQueryKey = (filters: NotificationFilters) =>
  [...NOTIFICATIONS_QUERY_KEY, 'list', filters] as const;
export const notificationUnreadCountQueryKey = [
  ...NOTIFICATIONS_QUERY_KEY,
  'unread-count',
] as const;

function useInvalidateNotifications() {
  const queryClient = useQueryClient();
  return () => queryClient.invalidateQueries({ queryKey: NOTIFICATIONS_QUERY_KEY });
}

export function useNotifications(filters: NotificationFilters = {}) {
  return useQuery({
    queryKey: notificationListQueryKey(filters),
    queryFn: () => listNotificationsRequest(filters),
  });
}

/**
 * Backs the notification bell's unread badge. Polled rather than pushed —
 * ARCHITECTURE.md Section 6 calls out polling through TanStack Query as the
 * initial approach for real-time needs like live notifications, with
 * WebSockets/SSE as a future upgrade path, not required at this milestone.
 */
export function useUnreadNotificationCount() {
  return useQuery({
    queryKey: notificationUnreadCountQueryKey,
    queryFn: getUnreadCountRequest,
    refetchInterval: 30_000,
  });
}

export function useMarkNotificationRead() {
  const invalidateNotifications = useInvalidateNotifications();

  return useMutation({
    mutationFn: ({ notificationId, isRead }: { notificationId: string; isRead: boolean }) =>
      updateNotificationReadStateRequest(notificationId, isRead),
    onSuccess: invalidateNotifications,
  });
}

export function useMarkAllNotificationsRead() {
  const invalidateNotifications = useInvalidateNotifications();

  return useMutation({
    mutationFn: markAllNotificationsReadRequest,
    onSuccess: invalidateNotifications,
  });
}

export function useDeleteNotification() {
  const invalidateNotifications = useInvalidateNotifications();

  return useMutation({
    mutationFn: (notificationId: string) => deleteNotificationRequest(notificationId),
    onSuccess: invalidateNotifications,
  });
}

export function useRegisterDeviceToken() {
  return useMutation({
    mutationFn: (payload: DeviceTokenPayload) => registerDeviceTokenRequest(payload),
  });
}

export function useUnregisterDeviceToken() {
  return useMutation({
    mutationFn: (deviceId: string) => unregisterDeviceTokenRequest(deviceId),
  });
}
