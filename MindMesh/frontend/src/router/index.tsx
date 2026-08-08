import { createBrowserRouter } from 'react-router-dom';
import { AppLayout } from '@/components/layout/AppLayout';
import { HomePage } from '@/components/pages/HomePage';
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
import { ProtectedRoute } from '@/router/ProtectedRoute';
import { ROUTES } from '@/constants';

/**
 * Root router configuration.
 *
 * Per ARCHITECTURE.md Section 2: route-level code splitting is expected as
 * feature modules are added. At this stage, auth (login/register/password
 * reset), account management (profile/settings), and a placeholder
 * authenticated home route exist — further feature routes (tasks, calendar,
 * notes, AI chat, etc.) are added starting in later milestones.
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
          { index: true, element: <HomePage /> },
          { path: ROUTES.PROFILE.slice(1), element: <ProfilePage /> },
          { path: ROUTES.SETTINGS.slice(1), element: <SettingsPage /> },
        ],
      },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
]);
