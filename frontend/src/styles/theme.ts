/**
 * MindMesh design tokens.
 *
 * Kept minimal and calm per the product's design philosophy (PRD.md, Section 12 —
 * Accessibility Features; ARCHITECTURE.md, Section 2 — Frontend Architecture).
 * These mirror the Tailwind config (tailwind.config.js) and should stay in sync
 * with it as the design system evolves.
 */

export const theme = {
  colors: {
    brand: {
      50: '#f5f7ff',
      100: '#ebeeff',
      200: '#d4daff',
      300: '#b0bbff',
      400: '#8593ff',
      500: '#5f6dfa',
      600: '#4750e0',
      700: '#3a3fb8',
      800: '#333794',
      900: '#2e3277',
    },
  },
  fontFamily: {
    sans: ['Inter', 'system-ui', 'sans-serif'],
  },
  radius: {
    sm: '0.375rem',
    md: '0.5rem',
    lg: '0.75rem',
    xl: '1rem',
  },
} as const;

export type Theme = typeof theme;
