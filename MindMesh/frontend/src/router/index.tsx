import { createBrowserRouter } from 'react-router-dom';
import { AppLayout } from '@/components/layout/AppLayout';
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
import { ChatPage } from '@/features/ai-chat';
import { CalendarPage } from '@/features/calendar';
import { DashboardPage } from '@/features/dashboard';
import { NotesPage } from '@/features/notes';
import { TasksPage } from '@/features/tasks';
import { ProtectedRoute } from '@/router/ProtectedRoute';
import { ROUTES } from '@/constants';

/**
 * Root router configuration.
 *
 * Per ARCHITECTURE.md Section 2: route-level code splitting is expected as
 * feature modules are added. At this stage, auth (login/register/password
 * reset), account management (profile/settings), the dashboard (home),
 * Tasks (ROADMAP.md Milestone 4), Calendar & Scheduling (Milestone 5),
 * Notes & Knowledge (Milestone 6), and the AI Companion (Milestone 7) all
 * exist. AI Chat graduated off the ComingSoonPage stub that occupied
 * ROUTES.AI_CHAT since Milestone 3.
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
            element: <NotesPage />,
          },
          {
            path: ROUTES.CALENDAR.slice(1),
            element: <CalendarPage />,
          },
          {
            path: ROUTES.AI_CHAT.slice(1),
            element: <ChatPage />,
          },
        ],
      },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
]);
