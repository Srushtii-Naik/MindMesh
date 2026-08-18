import { useState } from 'react';
import {
  useDeleteNotification,
  useMarkAllNotificationsRead,
  useMarkNotificationRead,
  useNotifications,
} from '@/features/notifications/hooks';
import type { NotificationFilters } from '@/features/notifications/types';

function formatNotificationTime(value: string): string {
  return new Date(value).toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  });
}

const ALL_FILTER: NotificationFilters = {};

/**
 * Full notification center (ROADMAP.md Milestone 9). NotificationBell in
 * AppHeader shows a quick preview; this is the "View all" destination with
 * read/unread filtering and dismissal.
 */
export function NotificationList() {
  const [showUnreadOnly, setShowUnreadOnly] = useState(false);

  const filters: NotificationFilters = showUnreadOnly ? { is_read: false } : ALL_FILTER;
  const { data, isLoading, isError } = useNotifications(filters);
  const markRead = useMarkNotificationRead();
  const markAllRead = useMarkAllNotificationsRead();
  const deleteNotification = useDeleteNotification();

  const notifications = data?.results ?? [];

  return (
    <section className="mx-auto flex max-w-2xl flex-col gap-4 px-4 py-8 sm:px-6 lg:px-8">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold text-slate-900 dark:text-slate-100">Notifications</h1>
        <div className="flex items-center gap-3">
          <label className="flex items-center gap-1.5 text-sm text-slate-600 dark:text-slate-300">
            <input
              type="checkbox"
              checked={showUnreadOnly}
              onChange={(event) => setShowUnreadOnly(event.target.checked)}
              className="rounded border-slate-300 text-brand-600 focus:ring-brand-500"
            />
            Unread only
          </label>
          <button
            type="button"
            onClick={() => markAllRead.mutate()}
            disabled={markAllRead.isPending}
            className="text-sm font-medium text-brand-600 hover:underline disabled:opacity-60 dark:text-brand-400"
          >
            Mark all read
          </button>
        </div>
      </div>

      {isLoading && <p className="text-sm text-slate-500 dark:text-slate-400">Loading…</p>}
      {isError && (
        <p className="text-sm text-red-600 dark:text-red-400">Couldn&apos;t load notifications.</p>
      )}
      {!isLoading && !isError && notifications.length === 0 && (
        <p className="text-sm text-slate-500 dark:text-slate-400">
          {showUnreadOnly ? 'No unread notifications.' : 'No notifications yet.'}
        </p>
      )}

      <ul className="flex flex-col gap-2">
        {notifications.map((notification) => (
          <li
            key={notification.id}
            className="flex items-start justify-between gap-3 rounded-lg border border-slate-200 bg-white p-3 dark:border-slate-700 dark:bg-slate-800"
          >
            <div className="min-w-0">
              <div className="flex items-center gap-2">
                {!notification.is_read && (
                  <span
                    aria-hidden="true"
                    className="h-1.5 w-1.5 shrink-0 rounded-full bg-brand-600 dark:bg-brand-400"
                  />
                )}
                <p className="truncate text-sm font-medium text-slate-900 dark:text-slate-100">
                  {notification.title}
                </p>
              </div>
              {notification.message && (
                <p className="mt-0.5 text-sm text-slate-600 dark:text-slate-300">
                  {notification.message}
                </p>
              )}
              <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
                {formatNotificationTime(notification.created_at)}
              </p>
            </div>

            <div className="flex shrink-0 flex-col items-end gap-1">
              {!notification.is_read && (
                <button
                  type="button"
                  onClick={() => markRead.mutate({ notificationId: notification.id, isRead: true })}
                  className="text-xs font-medium text-brand-600 hover:underline dark:text-brand-400"
                >
                  Mark read
                </button>
              )}
              <button
                type="button"
                onClick={() => deleteNotification.mutate(notification.id)}
                className="text-xs font-medium text-slate-500 hover:text-red-600 dark:text-slate-400 dark:hover:text-red-400"
              >
                Dismiss
              </button>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
