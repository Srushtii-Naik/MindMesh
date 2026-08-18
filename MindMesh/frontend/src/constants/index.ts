/**
 * Application-wide constants.
 * Feature-specific constants belong inside their respective `features/<domain>` module.
 */

export const APP_NAME = 'MindMesh';

export const API_BASE_URL: string =
  import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1';

export const API_TIMEOUT_MS: number = Number(import.meta.env.VITE_API_TIMEOUT_MS ?? 15000);

export const APP_ENV: 'development' | 'staging' | 'production' =
  (import.meta.env.VITE_APP_ENV as 'development' | 'staging' | 'production') ?? 'development';

/** Route path constants — extended as feature modules are added. */
export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  FORGOT_PASSWORD: '/forgot-password',
  RESET_PASSWORD: '/reset-password',
  PROFILE: '/profile',
  SETTINGS: '/settings',
  // Quick-action targets for modules not yet built (ROADMAP.md Milestone 3:
  // "Quick actions route correctly to their respective modules (stubbed if
  // modules not yet built)"). Each renders a placeholder until its own
  // milestone (4, 6, 5, 7 respectively) implements it for real.
  TASKS: '/tasks',
  NOTES: '/notes',
  CALENDAR: '/calendar',
  AI_CHAT: '/chat',
  NOTIFICATIONS: '/notifications',
  FAMILY: '/family',
  NOT_FOUND: '*',
} as const;
