import { lazy, Suspense } from 'react';
import { createBrowserRouter } from 'react-router-dom';
import { AppLayout } from '@/components/layout/AppLayout';
import { NotFoundPage } from '@/components/pages/NotFoundPage';
import { AuthLayout } from '@/features/auth';
import { ProtectedRoute } from '@/router/ProtectedRoute';
import { ROUTES } from '@/constants';

/**
 * Root router configuration.
 *
 * Per ARCHITECTURE.md Section 2 ("route-level code splitting for
 * performance") and PROJECT_RULES.md Section 11 ("Lazy loading. Route-level
 * code splitting is used throughout the frontend; nothing is loaded before
 * it's needed"): every routed page is a separate `React.lazy` chunk rather
 * than a top-level import, so the initial bundle only contains what's
 * needed to render the first screen — the auth pages (~always needed
 * first) plus routing/layout shells. Everything else (tasks, notes,
 * calendar, AI chat, notifications, family, analytics, profile/settings)
 * loads on first navigation to that route.
 */
const LoginPage = lazy(() => import('@/features/auth').then((m) => ({ default: m.LoginPage })));
const RegisterPage = lazy(() =>
  import('@/features/auth').then((m) => ({ default: m.RegisterPage }))
);
const ForgotPasswordPage = lazy(() =>
  import('@/features/auth').then((m) => ({ default: m.ForgotPasswordPage }))
);
const ResetPasswordPage = lazy(() =>
  import('@/features/auth').then((m) => ({ default: m.ResetPasswordPage }))
);
const ProfilePage = lazy(() => import('@/features/auth').then((m) => ({ default: m.ProfilePage })));
const SettingsPage = lazy(() =>
  import('@/features/auth').then((m) => ({ default: m.SettingsPage }))
);
const AnalyticsPage = lazy(() =>
  import('@/features/analytics').then((m) => ({ default: m.AnalyticsPage }))
);
const ChatPage = lazy(() => import('@/features/ai-chat').then((m) => ({ default: m.ChatPage })));
const CalendarPage = lazy(() =>
  import('@/features/calendar').then((m) => ({ default: m.CalendarPage }))
);
const DashboardPage = lazy(() =>
  import('@/features/dashboard').then((m) => ({ default: m.DashboardPage }))
);
const FamilyPage = lazy(() => import('@/features/family').then((m) => ({ default: m.FamilyPage })));
const NotesPage = lazy(() => import('@/features/notes').then((m) => ({ default: m.NotesPage })));
const NotificationsPage = lazy(() =>
  import('@/features/notifications').then((m) => ({ default: m.NotificationsPage }))
);
const TasksPage = lazy(() => import('@/features/tasks').then((m) => ({ default: m.TasksPage })));

/**
 * Minimal, unstyled fallback for the brief moment a route chunk is
 * downloading — per PROJECT_RULES.md Section 5, motion/loading states must
 * stay calm and never call attention to themselves, so this intentionally
 * has no spinner animation. Defined as an element (not a component
 * function) since this module's main export is the router config, not a
 * component — see the react-refresh/only-export-components lint rule.
 */
const routeFallback = <div aria-busy="true" aria-live="polite" />;

function withSuspense(element: React.ReactNode) {
  return <Suspense fallback={routeFallback}>{element}</Suspense>;
}

export const router = createBrowserRouter([
  {
    element: <AuthLayout />,
    children: [
      { path: ROUTES.LOGIN, element: withSuspense(<LoginPage />) },
      { path: ROUTES.REGISTER, element: withSuspense(<RegisterPage />) },
      { path: ROUTES.FORGOT_PASSWORD, element: withSuspense(<ForgotPasswordPage />) },
      { path: ROUTES.RESET_PASSWORD, element: withSuspense(<ResetPasswordPage />) },
    ],
  },
  {
    path: '/',
    element: <AppLayout />,
    children: [
      {
        element: <ProtectedRoute />,
        children: [
          { index: true, element: withSuspense(<DashboardPage />) },
          { path: ROUTES.PROFILE.slice(1), element: withSuspense(<ProfilePage />) },
          { path: ROUTES.SETTINGS.slice(1), element: withSuspense(<SettingsPage />) },
          { path: ROUTES.TASKS.slice(1), element: withSuspense(<TasksPage />) },
          { path: ROUTES.NOTES.slice(1), element: withSuspense(<NotesPage />) },
          { path: ROUTES.CALENDAR.slice(1), element: withSuspense(<CalendarPage />) },
          { path: ROUTES.AI_CHAT.slice(1), element: withSuspense(<ChatPage />) },
          {
            path: ROUTES.NOTIFICATIONS.slice(1),
            element: withSuspense(<NotificationsPage />),
          },
          { path: ROUTES.FAMILY.slice(1), element: withSuspense(<FamilyPage />) },
          { path: ROUTES.ANALYTICS.slice(1), element: withSuspense(<AnalyticsPage />) },
        ],
      },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
]);
