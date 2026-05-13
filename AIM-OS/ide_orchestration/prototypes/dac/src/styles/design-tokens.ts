/**
 * AIM-OS Design System Tokens (TypeScript)
 * Programmatic access to design tokens for TypeScript/JavaScript
 */

export const designTokens = {
  // Background Colors
  bg: {
    primary: '#030712',
    secondary: '#111827',
    tertiary: '#1f2937',
    elevated: '#374151',
    hover: '#4b5563',
  },

  // Text Colors
  text: {
    primary: '#f3f4f6',
    secondary: '#9ca3af',
    tertiary: '#6b7280',
    disabled: '#4b5563',
  },

  // Border Colors
  border: {
    primary: '#374151',
    secondary: '#4b5563',
    subtle: '#1f2937',
  },

  // Semantic Colors
  success: {
    DEFAULT: '#10b981',
    dark: '#059669',
    light: '#34d399',
    bg: 'rgba(16, 185, 129, 0.1)',
  },
  warning: {
    DEFAULT: '#f59e0b',
    dark: '#d97706',
    light: '#fbbf24',
    bg: 'rgba(245, 158, 11, 0.1)',
  },
  error: {
    DEFAULT: '#ef4444',
    dark: '#dc2626',
    light: '#f87171',
    bg: 'rgba(239, 68, 68, 0.1)',
  },
  info: {
    DEFAULT: '#3b82f6',
    dark: '#2563eb',
    light: '#60a5fa',
    bg: 'rgba(59, 130, 246, 0.1)',
  },

  // AIM-OS System Colors
  cmc: {
    DEFAULT: '#7ee787',
    dark: '#56d364',
    light: '#a0e7a0',
    bg: 'rgba(126, 231, 135, 0.1)',
  },
  hhni: {
    DEFAULT: '#79c0ff',
    dark: '#58a6ff',
    light: '#a5d6ff',
    bg: 'rgba(121, 192, 255, 0.1)',
  },
  vif: {
    DEFAULT: '#ffa657',
    dark: '#ff8c42',
    light: '#ffc085',
    bg: 'rgba(255, 166, 87, 0.1)',
  },
  apoe: {
    DEFAULT: '#d2a8ff',
    dark: '#b87fff',
    light: '#e6cfff',
    bg: 'rgba(210, 168, 255, 0.1)',
  },
  seg: {
    DEFAULT: '#ff7b72',
    dark: '#ff5d52',
    light: '#ff9d95',
    bg: 'rgba(255, 123, 114, 0.1)',
  },
  cas: {
    DEFAULT: '#4ec9b0',
    dark: '#3db89a',
    light: '#6dd9c4',
    bg: 'rgba(78, 201, 176, 0.1)',
  },
  tcs: {
    DEFAULT: '#569cd6',
    dark: '#3d8bc4',
    light: '#7ab3e8',
    bg: 'rgba(86, 156, 214, 0.1)',
  },
  scor: {
    DEFAULT: '#f44747',
    dark: '#d32f2f',
    light: '#ff6b6b',
    bg: 'rgba(244, 71, 71, 0.1)',
  },

  // Interactive Colors
  primary: {
    DEFAULT: '#3b82f6',
    hover: '#2563eb',
    active: '#1d4ed8',
    disabled: '#1e3a8a',
  },
  secondary: {
    DEFAULT: '#8b5cf6',
    hover: '#7c3aed',
    active: '#6d28d9',
  },
  accent: {
    DEFAULT: '#ec4899',
    hover: '#db2777',
    active: '#be185d',
  },

  // Typography
  font: {
    primary: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif",
    mono: "'JetBrains Mono', 'Fira Code', 'Consolas', 'Courier New', monospace",
    display: "'Inter', sans-serif",
  },
  fontSize: {
    xs: '0.75rem',      // 12px
    sm: '0.875rem',    // 14px
    base: '1rem',      // 16px
    lg: '1.125rem',    // 18px
    xl: '1.25rem',     // 20px
    '2xl': '1.5rem',   // 24px
    '3xl': '1.875rem', // 30px
    '4xl': '2.25rem',  // 36px
  },
  lineHeight: {
    tight: 1.25,
    normal: 1.5,
    relaxed: 1.75,
  },
  fontWeight: {
    light: 300,
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },

  // Spacing (8px base)
  spacing: {
    0: '0',
    1: '0.25rem',   // 4px
    2: '0.5rem',    // 8px
    3: '0.75rem',   // 12px
    4: '1rem',      // 16px
    5: '1.25rem',   // 20px
    6: '1.5rem',   // 24px
    8: '2rem',      // 32px
    10: '2.5rem',   // 40px
    12: '3rem',     // 48px
    16: '4rem',     // 64px
    20: '5rem',     // 80px
    24: '6rem',     // 96px
  },

  // Layout
  container: {
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1280px',
    '2xl': '1536px',
  },
  borderRadius: {
    sm: '0.25rem',   // 4px
    md: '0.5rem',    // 8px
    lg: '0.75rem',   // 12px
    xl: '1rem',      // 16px
    full: '9999px',  // Full circle
  },

  // Shadows
  shadow: {
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
    '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
  },
  depth: {
    0: 'none',
    1: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    2: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    3: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    4: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
    5: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
  },

  // Transitions
  transition: {
    fast: '150ms',
    base: '200ms',
    slow: '300ms',
    slower: '500ms',
  },
  easing: {
    in: 'cubic-bezier(0.4, 0, 1, 1)',
    out: 'cubic-bezier(0, 0, 0.2, 1)',
    'in-out': 'cubic-bezier(0.4, 0, 0.2, 1)',
    standard: 'cubic-bezier(0.4, 0, 0.2, 1)',
  },
} as const;

/**
 * Get CSS variable name for a design token
 */
export function getCSSVariable(path: string[]): string {
  return `--aimos-${path.join('-')}`;
}

/**
 * Get design token value
 */
export function getToken(path: string[]): string {
  let value: any = designTokens;
  for (const key of path) {
    value = value[key];
    if (value === undefined) {
      throw new Error(`Token not found: ${path.join('.')}`);
    }
  }
  return typeof value === 'string' ? value : String(value);
}

/**
 * Get AIM-OS system color by name
 */
export function getSystemColor(system: 'cmc' | 'hhni' | 'vif' | 'apoe' | 'seg' | 'cas' | 'tcs' | 'scor'): string {
  return designTokens[system].DEFAULT;
}

/**
 * Icon sizes (for lucide-react)
 */
export const iconSizes = {
  xs: 'w-3 h-3',    // 12px
  sm: 'w-4 h-4',    // 16px
  md: 'w-5 h-5',    // 20px
  lg: 'w-6 h-6',    // 24px
  xl: 'w-8 h-8',    // 32px
  '2xl': 'w-12 h-12' // 48px
} as const;

export type IconSize = keyof typeof iconSizes;

