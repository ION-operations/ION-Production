import type { Config } from 'tailwindcss'

export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      // AIM-OS Design System Colors
      colors: {
        // Backgrounds
        'aimos-bg': {
          primary: '#030712',
          secondary: '#111827',
          tertiary: '#1f2937',
          elevated: '#374151',
          hover: '#4b5563',
        },
        // Text
        'aimos-text': {
          primary: '#f3f4f6',
          secondary: '#9ca3af',
          tertiary: '#6b7280',
          disabled: '#4b5563',
        },
        // Borders
        'aimos-border': {
          primary: '#374151',
          secondary: '#4b5563',
          subtle: '#1f2937',
        },
        // Semantic Colors
        'aimos-success': {
          DEFAULT: '#10b981',
          dark: '#059669',
          light: '#34d399',
        },
        'aimos-warning': {
          DEFAULT: '#f59e0b',
          dark: '#d97706',
          light: '#fbbf24',
        },
        'aimos-error': {
          DEFAULT: '#ef4444',
          dark: '#dc2626',
          light: '#f87171',
        },
        'aimos-info': {
          DEFAULT: '#3b82f6',
          dark: '#2563eb',
          light: '#60a5fa',
        },
        // AIM-OS System Colors
        'aimos-cmc': {
          DEFAULT: '#7ee787',
          dark: '#56d364',
          light: '#a0e7a0',
        },
        'aimos-hhni': {
          DEFAULT: '#79c0ff',
          dark: '#58a6ff',
          light: '#a5d6ff',
        },
        'aimos-vif': {
          DEFAULT: '#ffa657',
          dark: '#ff8c42',
          light: '#ffc085',
        },
        'aimos-apoe': {
          DEFAULT: '#d2a8ff',
          dark: '#b87fff',
          light: '#e6cfff',
        },
        'aimos-seg': {
          DEFAULT: '#ff7b72',
          dark: '#ff5d52',
          light: '#ff9d95',
        },
        'aimos-cas': {
          DEFAULT: '#4ec9b0',
          dark: '#3db89a',
          light: '#6dd9c4',
        },
        'aimos-tcs': {
          DEFAULT: '#569cd6',
          dark: '#3d8bc4',
          light: '#7ab3e8',
        },
        'aimos-scor': {
          DEFAULT: '#f44747',
          dark: '#d32f2f',
          light: '#ff6b6b',
        },
        // Interactive Colors
        'aimos-primary': {
          DEFAULT: '#3b82f6',
          hover: '#2563eb',
          active: '#1d4ed8',
          disabled: '#1e3a8a',
        },
        'aimos-secondary': {
          DEFAULT: '#8b5cf6',
          hover: '#7c3aed',
          active: '#6d28d9',
        },
        'aimos-accent': {
          DEFAULT: '#ec4899',
          hover: '#db2777',
          active: '#be185d',
        },
      },
      // Typography
      fontFamily: {
        'aimos': ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', 'sans-serif'],
        'aimos-mono': ['JetBrains Mono', 'Fira Code', 'Consolas', 'Courier New', 'monospace'],
        'aimos-display': ['Inter', 'sans-serif'],
      },
      fontSize: {
        'aimos-xs': ['0.75rem', { lineHeight: '1.5' }],
        'aimos-sm': ['0.875rem', { lineHeight: '1.5' }],
        'aimos-base': ['1rem', { lineHeight: '1.5' }],
        'aimos-lg': ['1.125rem', { lineHeight: '1.5' }],
        'aimos-xl': ['1.25rem', { lineHeight: '1.5' }],
        'aimos-2xl': ['1.5rem', { lineHeight: '1.25' }],
        'aimos-3xl': ['1.875rem', { lineHeight: '1.25' }],
        'aimos-4xl': ['2.25rem', { lineHeight: '1.25' }],
      },
      fontWeight: {
        'aimos-light': '300',
        'aimos-normal': '400',
        'aimos-medium': '500',
        'aimos-semibold': '600',
        'aimos-bold': '700',
      },
      // Spacing (8px base)
      spacing: {
        'aimos-0': '0',
        'aimos-1': '0.25rem',   // 4px
        'aimos-2': '0.5rem',     // 8px
        'aimos-3': '0.75rem',    // 12px
        'aimos-4': '1rem',       // 16px
        'aimos-5': '1.25rem',    // 20px
        'aimos-6': '1.5rem',     // 24px
        'aimos-8': '2rem',       // 32px
        'aimos-10': '2.5rem',    // 40px
        'aimos-12': '3rem',      // 48px
        'aimos-16': '4rem',      // 64px
        'aimos-20': '5rem',      // 80px
        'aimos-24': '6rem',      // 96px
      },
      // Border Radius
      borderRadius: {
        'aimos-sm': '0.25rem',   // 4px
        'aimos-md': '0.5rem',    // 8px
        'aimos-lg': '0.75rem',   // 12px
        'aimos-xl': '1rem',      // 16px
      },
      // Shadows
      boxShadow: {
        'aimos-sm': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        'aimos-md': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        'aimos-lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
        'aimos-xl': '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
        'aimos-2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
      },
      // Transitions
      transitionDuration: {
        'aimos-fast': '150ms',
        'aimos-base': '200ms',
        'aimos-slow': '300ms',
        'aimos-slower': '500ms',
      },
      transitionTimingFunction: {
        'aimos-in': 'cubic-bezier(0.4, 0, 1, 1)',
        'aimos-out': 'cubic-bezier(0, 0, 0.2, 1)',
        'aimos-in-out': 'cubic-bezier(0.4, 0, 0.2, 1)',
        'aimos-standard': 'cubic-bezier(0.4, 0, 0.2, 1)',
      },
    },
  },
  plugins: [],
} satisfies Config

