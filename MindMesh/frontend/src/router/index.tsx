import { createBrowserRouter } from 'react-router-dom';
import { AppLayout } from '@/components/layout/AppLayout';
import { ComingSoonPage } from '@/components/pages/ComingSoonPage';
import { NotFoundPage } from '@/components/pages/NotFoundPage';
import {
  AuthLayout,
  LoginPage,
  RegisterPage,
  ForgotPasswordPage,
  ResetPasswordPage,
  ProfilePage,
  SettingsPage,
} from '@/features/auth';
import { DashboardPage } from '@/features/dashboard';
import { TasksPage } from '@/features/tasks';
import { ProtectedRoute } from '@/router/ProtectedRoute';
import { ROUTES } from '@/constants';

/**
 * Root router configuration.
 *
 * Per ARCHITECTURE.md Section 2: route-level code splitting is expected as
 * feature modules are added. At this stage, auth (login/register/password
 * reset), account management (profile/settings), the dashboard (home), and
 * Tasks (ROADMAP.md Milestone 4) exist. Notes/Calendar/AI Chat remain
 * stubbed with ComingSoonPage as quick-action targets until their own
 * milestones (6, 5, 7) build them.
 */
export const router = createBrowserRouter([
  {
    element: <AuthLayout />,
    children: [
      { path: ROUTES.LOGIN, element: <LoginPage /> },
      { path: ROUTES.REGISTER, element: <RegisterPage /> },
      { path: ROUTES.FORGOT_PASSWORD, element: <ForgotPasswordPage /> },
      { path: ROUTES.RESET_PASSWORD, element: <ResetPasswordPage /> },
    ],
  },
  {
    path: '/',
    element: <AppLayout />,
    children: [
      {
        element: <ProtectedRoute />,
        children: [
          { index: true, element: <DashboardPage /> },
          { path: ROUTES.PROFILE.slice(1), element: <ProfilePage /> },
          { path: ROUTES.SETTINGS.slice(1), element: <SettingsPage /> },
          { path: ROUTES.TASKS.slice(1), element: <TasksPage /> },
          {
            path: ROUTES.NOTES.slice(1),
            element: (
              <ComingSoonPage
                title="Notes"
                description="Notes & knowledge capture is coming in a future milestone."
              />
            ),
          },
          {
            path: ROUTES.CALENDAR.slice(1),
            element: (
              <ComingSoonPage
                title="Calendar"
                description="Calendar & scheduling is coming in a future milestone."
              />
            ),
          },
          {
            path: ROUTES.AI_CHAT.slice(1),
            element: (
              <ComingSoonPage
                title="AI Companion"
                description="Your AI companion chat is coming in a future milestone."
              />
            ),
          },
        ],
      },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
]);
