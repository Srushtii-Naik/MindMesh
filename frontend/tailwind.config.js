/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // MindMesh design tokens — extend as the design system matures.
        // Kept minimal and calm per PROJECT_RULES.md design philosophy.
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
    },
  },
  plugins: [],
};
