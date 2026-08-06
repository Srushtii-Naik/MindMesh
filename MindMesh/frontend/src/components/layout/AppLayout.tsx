import { Outlet } from 'react-router-dom';

/**
 * Root application shell.
 * Feature navigation (sidebar, module switcher, notification center, etc.)
 * is intentionally deferred to later milestones per ROADMAP.md.
 */
export function AppLayout() {
  return (
    <div className="flex min-h-screen flex-col">
      <main className="flex-1">
        <Outlet />
      </main>
    </div>
  );
}
