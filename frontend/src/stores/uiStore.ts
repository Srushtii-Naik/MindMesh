import { create } from 'zustand';

/**
 * Global UI/local state store (Zustand).
 * Per ARCHITECTURE.md Section 2: UI/local/session state (theme, active view, modals,
 * ephemeral form state) is managed here — distinct from server state, which is
 * owned by TanStack Query.
 *
 * Feature-specific UI state should live in its own store inside `features/<domain>`.
 */
interface UIState {
  isSidebarOpen: boolean;
  theme: 'light' | 'dark';
  toggleSidebar: () => void;
  setTheme: (theme: 'light' | 'dark') => void;
}

export const useUIStore = create<UIState>((set) => ({
  isSidebarOpen: false,
  theme: 'light',
  toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
  setTheme: (theme) => set({ theme }),
}));
