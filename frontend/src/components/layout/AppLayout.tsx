import { Outlet } from 'react-router-dom';
import { AppHeader } from '@/components/layout/AppHeader';

/**
 * Root application shell.
 * Milestone 3 introduces AppHeader (nav + sign out) as the shared shell
 * across authenticated pages — see AppHeader.tsx.
 */
export function AppLayout() {
  return (
    <div className="flex min-h-screen flex-col">
      <AppHeader />
      <main className="flex-1">
        <Outlet />
      </main>
    </div>
  );
}
