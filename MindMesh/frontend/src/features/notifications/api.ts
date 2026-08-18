import { apiClient } from '@/api/client';
import type { PaginatedResponse } from '@/types';
import type {
  DeviceToken,
  DeviceTokenPayload,
  Notification,
  NotificationFilters,
} from '@/features/notifications/types';

/**
 * Notifications domain requests (ROADMAP.md Milestone 9 — the in-app
 * notification center, plus push device registration). Consumed
 * exclusively via the TanStack Query hooks in `features/notifications/hooks/`,
 * per ARCHITECTURE.md Section 2.
 */

export async function listNotificationsRequest(
  filters: NotificationFilters
): Promise<PaginatedResponse<Notification>> {
  const { data } = await apiClient.get<PaginatedResponse<Notification>>('/notifications/', {
    params: filters,
  });
  return data;
}

export async function getUnreadCountRequest(): Promise<number> {
  const { data } = await apiClient.get<{ unread_count: number }>('/notifications/unread-count/');
  return data.unread_count;
}

export async function updateNotificationReadStateRequest(
  notificationId: string,
  isRead: boolean
): Promise<Notification> {
  const { data } = await apiClient.patch<Notification>(`/notifications/${notificationId}/`, {
    is_read: isRead,
  });
  return data;
}

export async function markAllNotificationsReadRequest(): Promise<{ updated: number }> {
  const { data } = await apiClient.post<{ updated: number }>('/notifications/mark-all-read/');
  return data;
}

export async function deleteNotificationRequest(notificationId: string): Promise<void> {
  await apiClient.delete(`/notifications/${notificationId}/`);
}

export async function registerDeviceTokenRequest(
  payload: DeviceTokenPayload
): Promise<DeviceToken> {
  const { data } = await apiClient.post<DeviceToken>('/notifications/devices/', payload);
  return data;
}

export async function unregisterDeviceTokenRequest(deviceId: string): Promise<void> {
  await apiClient.delete(`/notifications/devices/${deviceId}/`);
}
