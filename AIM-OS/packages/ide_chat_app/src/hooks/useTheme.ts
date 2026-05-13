/**
 * Theme System
 * 
 * Phase 5.3: Visual Polish - Theme Management
 * 
 * Features:
 * - Multiple theme support (dark, light, high-contrast)
 * - Theme persistence
 * - Smooth theme transitions
 * - Custom theme variables
 */

import { useState, useEffect, useMemo } from 'react'

export type Theme = 'dark' | 'light' | 'high-contrast' | 'auto'

export interface ThemeConfig {
  name: Theme
  colors: {
    background: string
    surface: string
    text: string
    textSecondary: string
    border: string
    primary: string
    primaryHover: string
    secondary: string
    error: string
    warning: string
    success: string
    info: string
  }
}

const themes: Record<Theme, ThemeConfig> = {
  dark: {
    name: 'dark',
    colors: {
      background: '#111827',
      surface: '#1F2937',
      text: '#F9FAFB',
      textSecondary: '#9CA3AF',
      border: '#374151',
      primary: '#3B82F6',
      primaryHover: '#2563EB',
      secondary: '#8B5CF6',
      error: '#EF4444',
      warning: '#F59E0B',
      success: '#10B981',
      info: '#06B6D4',
    },
  },
  light: {
    name: 'light',
    colors: {
      background: '#FFFFFF',
      surface: '#F9FAFB',
      text: '#111827',
      textSecondary: '#6B7280',
      border: '#E5E7EB',
      primary: '#3B82F6',
      primaryHover: '#2563EB',
      secondary: '#8B5CF6',
      error: '#EF4444',
      warning: '#F59E0B',
      success: '#10B981',
      info: '#06B6D4',
    },
  },
  'high-contrast': {
    name: 'high-contrast',
    colors: {
      background: '#000000',
      surface: '#1A1A1A',
      text: '#FFFFFF',
      textSecondary: '#CCCCCC',
      border: '#666666',
      primary: '#00FFFF',
      primaryHover: '#00CCCC',
      secondary: '#FF00FF',
      error: '#FF0000',
      warning: '#FFFF00',
      success: '#00FF00',
      info: '#00FFFF',
    },
  },
  auto: {
    name: 'auto',
    colors: {
      background: '#111827',
      surface: '#1F2937',
      text: '#F9FAFB',
      textSecondary: '#9CA3AF',
      border: '#374151',
      primary: '#3B82F6',
      primaryHover: '#2563EB',
      secondary: '#8B5CF6',
      error: '#EF4444',
      warning: '#F59E0B',
      success: '#10B981',
      info: '#06B6D4',
    },
  },
}

export const useTheme = () => {
  const [theme, setTheme] = useState<Theme>(() => {
    if (typeof window === 'undefined') return 'dark'
    const stored = localStorage.getItem('rev-ide-theme') as Theme | null
    return stored || 'dark'
  })

  const [resolvedTheme, setResolvedTheme] = useState<Exclude<Theme, 'auto'>>('dark')

  // Resolve auto theme
  useEffect(() => {
    if (theme === 'auto') {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      setResolvedTheme(prefersDark ? 'dark' : 'light')

      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
      const handleChange = (e: MediaQueryListEvent) => {
        setResolvedTheme(e.matches ? 'dark' : 'light')
      }

      mediaQuery.addEventListener('change', handleChange)
      return () => mediaQuery.removeEventListener('change', handleChange)
    } else {
      setResolvedTheme(theme as Exclude<Theme, 'auto'>)
    }
  }, [theme])

  // Apply theme to document
  useEffect(() => {
    const themeConfig = themes[resolvedTheme]
    const root = document.documentElement

    Object.entries(themeConfig.colors).forEach(([key, value]) => {
      root.style.setProperty(`--color-${key}`, value)
    })

    root.setAttribute('data-theme', resolvedTheme)
    root.classList.remove('theme-dark', 'theme-light', 'theme-high-contrast')
    root.classList.add(`theme-${resolvedTheme}`)
  }, [resolvedTheme])

  // Persist theme
  useEffect(() => {
    localStorage.setItem('rev-ide-theme', theme)
  }, [theme])

  const currentTheme = useMemo(() => themes[resolvedTheme], [resolvedTheme])

  return {
    theme,
    resolvedTheme,
    currentTheme,
    setTheme,
    themes: Object.keys(themes) as Theme[],
  }
}

