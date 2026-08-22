import { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  useMarkAllNotificationsRead,
  useMarkNotificationRead,
  useNotifications,
  useUnreadNotificationCount,
} from '@/features/notifications/hooks';
import { ROUTES } from '@/constants';

function formatNotificationTime(value: string): string {
  return new Date(value).toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  });
}

/**
 * The in-app notification centers entry point (ROADMAP.md Milestone 9:
 * "In-app notification center reflects real-time and historical
 * notifications"). Lives in AppHeader so its available from every
 * authenticated page, mirroring how AppHeader already surfaces
 * Profile/Settings/Sign out globally rather than per-page.
 */
export function NotificationBell() {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const { data: unreadCount } = useUnreadNotificationCount();
  const { data, isLoading, isError } = useNotifications();
  const markRead = useMarkNotificationRead();
  const markAllRead = useMarkAllNotificationsRead();

  useEffect(() => {
    if (!isOpen) return;

    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen]);

  const hasUnread = Boolean(unreadCount && unreadCount > 0);
  const notifications = data?.results ?? [];

  return (
    <div ref={containerRef} className="relative">
      <button
        type="button"
        onClick={() => setIsOpen((open) => !open)}
        aria-label={hasUnread ? `Notifications (${unreadCount} unread)` : 'Notifications'}
        aria-expanded={isOpen}
        className="relative rounded-md p-1.5 text-slate-600 transition hover:bg-slate-100 hover:text-brand-600 dark:text-slate-300 dark:hover:bg-slate-800 dark:hover:text-brand-400"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth={1.75}
          className="h-5 w-5"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M14.857 17.082a23.848 23.848 0 0 0 5.454-1.31A8.967 8.967 0 0 1 18 9.75V9A6 6 0 0 0 6 9v.75a8.967 8.967 0 0 1-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 0 1-5.714 0m5.714 0a3 3 0 1 1-5.714 0"
          />
        </svg>
        {hasUnread && (
          <span
            data-testid="notification-badge"
            className="absolute -right-0.5 -top-0.5 flex h-4 min-w-[1rem] items-center justify-center rounded-full bg-red-600 px-1 text-[10px] font-semibold leading-none text-white"
          >
            {unreadCount && unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <div className="absolute right-0 z-20 mt-2 w-80 rounded-lg border border-slate-200 bg-white shadow-lg dark:border-slate-700 dark:bg-slate-800">
          <div className="flex items-center justify-between border-b border-slate-200 px-3 py-2 dark:border-slate-700">
            <h2 className="text-sm font-medium text-slate-700 dark:text-slate-300">
              Notifications
            </h2>
            {hasUnread && (
              <button
                type="button"
                onClick={() => markAllRead.mutate()}
                disabled={markAllRead.isPending}
                className="text-xs font-medium text-brand-600 hover:underline disabled:opacity-60 dark:text-brand-400"
              >
                Mark all read
              </button>
            )}
          </div>

          <div className="max-h-80 overflow-y-auto">
            {isLoading && (
              <p className="px-3 py-4 text-sm text-slate-500 dark:text-slate-400">Loading…</p>
            )}
            {isError && (
              <p className="px-3 py-4 text-sm text-red-600 dark:text-red-400">
                Couldn&apos;t load notifications.
              </p>
            )}
            {!isLoading && !isError && notifications.length === 0 && (
              <p className="px-3 py-4 text-sm text-slate-500 dark:text-slate-400">
                You&apos;re all caught up.
              </p>
            )}
            <ul>
              {notifications.map((notification) => (
                <li
                  key={notification.id}
                  className="border-b border-slate-100 px-3 py-2 last:border-0 dark:border-slate-700"
                >
                  <button
                    type="button"
                    onClick={() =>
                      !notification.is_read &&
                      markRead.mutate({ notificationId: notification.id, isRead: true })
                    }
                    className="flex w-full flex-col items-start gap-0.5 text-left"
                  >
                    <span className="flex w-full items-center gap-2">
                      {!notification.is_read && (
                        <span
                          aria-hidden="true"
                          className="h-1.5 w-1.5 shrink-0 rounded-full bg-brand-600 dark:bg-brand-400"
                        />
                      )}
                      <span className="truncate text-sm text-slate-900 dark:text-slate-100">
                        {notification.title}
                      </span>
                    </span>
                    <span className="text-xs text-slate-500 dark:text-slate-400">
                      {formatNotificationTime(notification.created_at)}
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          </div>

          <Link
            to={ROUTES.NOTIFICATIONS}
            onClick={() => setIsOpen(false)}
            className="block border-t border-slate-200 px-3 py-2 text-center text-xs font-medium text-brand-600 hover:underline dark:border-slate-700 dark:text-brand-400"
          >
            View all
          </Link>
        </div>
      )}
    </div>
  );
}
