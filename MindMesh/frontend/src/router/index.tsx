import { createBrowserRouter } from 'react-router-dom';
import { AppLayout } from '@/components/layout/AppLayout';
import { HomePage } from '@/components/pages/HomePage';
import { NotFoundPage } from '@/components/pages/NotFoundPage';

/**
 * Root router configuration.
 *
 * Per ARCHITECTURE.md Section 2: route-level code splitting is expected as
 * feature modules are added. At the Milestone 1 (Foundation) stage, only a
 * placeholder home route and a 404 route exist — feature routes (tasks,
 * calendar, notes, AI chat, etc.) are added starting in later milestones.
 */
export const router = createBrowserRouter([
  {
    path: '/',
    element: <AppLayout />,
    children: [
      { index: true, element: <HomePage /> },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
]);
