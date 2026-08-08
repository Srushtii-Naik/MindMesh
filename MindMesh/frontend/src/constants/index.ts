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
  NOT_FOUND: '*',
} as const;
