/**
 * Accessibility System
 * 
 * Phase 5.1: WCAG 2.1 AA Compliance
 * 
 * Features:
 * - Keyboard navigation support
 * - Screen reader support
 * - ARIA labels and roles
 * - Focus management
 * - Color contrast compliance
 * - Reduced motion support
 */

import React, { useEffect, useRef, useState } from 'react'

export interface AccessibilityConfig {
  enableKeyboardNavigation?: boolean
  enableScreenReader?: boolean
  enableReducedMotion?: boolean
  enableHighContrast?: boolean
  announcePageChanges?: boolean
}

const defaultConfig: AccessibilityConfig = {
  enableKeyboardNavigation: true,
  enableScreenReader: true,
  enableReducedMotion: false,
  enableHighContrast: false,
  announcePageChanges: true,
}

// Check for user preferences
export const getAccessibilityPreferences = (): AccessibilityConfig => {
  if (typeof window === 'undefined') return defaultConfig

  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  const prefersHighContrast = window.matchMedia('(prefers-contrast: high)').matches

  return {
    ...defaultConfig,
    enableReducedMotion: prefersReducedMotion,
    enableHighContrast: prefersHighContrast,
  }
}

// Keyboard navigation hook
export const useKeyboardNavigation = (
  items: Array<{ id: string }>,
  onSelect: (id: string) => void,
  enabled: boolean = true
) => {
  const [focusedIndex, setFocusedIndex] = useState<number | null>(null)
  const itemRefs = useRef<Map<string, HTMLElement>>(new Map())

  useEffect(() => {
    if (!enabled) return

    const handleKeyDown = (e: KeyboardEvent) => {
      if (focusedIndex === null) return

      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault()
          setFocusedIndex(prev => prev !== null ? Math.min(prev + 1, items.length - 1) : 0)
          break
        case 'ArrowUp':
          e.preventDefault()
          setFocusedIndex(prev => prev !== null ? Math.max(prev - 1, 0) : 0)
          break
        case 'Enter':
        case ' ':
          e.preventDefault()
          if (focusedIndex !== null && items[focusedIndex]) {
            onSelect(items[focusedIndex].id)
          }
          break
        case 'Home':
          e.preventDefault()
          setFocusedIndex(0)
          break
        case 'End':
          e.preventDefault()
          setFocusedIndex(items.length - 1)
          break
        case 'Escape':
          e.preventDefault()
          setFocusedIndex(null)
          break
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [enabled, focusedIndex, items, onSelect])

  // Focus element when index changes
  useEffect(() => {
    if (focusedIndex !== null && items[focusedIndex]) {
      const element = itemRefs.current.get(items[focusedIndex].id)
      if (element) {
        element.focus()
        element.scrollIntoView({ block: 'nearest', behavior: 'smooth' })
      }
    }
  }, [focusedIndex, items])

  return {
    focusedIndex,
    setFocusedIndex,
    itemRefs,
  }
}

// Screen reader announcements
export const useScreenReaderAnnouncement = (enabled: boolean = true) => {
  const announcementRef = useRef<HTMLDivElement>(null)

  const announce = (message: string, priority: 'polite' | 'assertive' = 'polite') => {
    if (!enabled || !announcementRef.current) return

    announcementRef.current.setAttribute('aria-live', priority)
    announcementRef.current.textContent = message

    // Clear after announcement
    setTimeout(() => {
      if (announcementRef.current) {
        announcementRef.current.textContent = ''
      }
    }, 1000)
  }

  return {
    announce,
    announcementRef,
  }
}

// Focus trap for modals
export const useFocusTrap = (enabled: boolean = true) => {
  const containerRef = useRef<HTMLElement | null>(null)

  useEffect(() => {
    if (!enabled || !containerRef.current) return

    const container = containerRef.current
    const focusableElements = container.querySelectorAll<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    )
    const firstElement = focusableElements[0]
    const lastElement = focusableElements[focusableElements.length - 1]

    const handleTab = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return

      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          e.preventDefault()
          lastElement?.focus()
        }
      } else {
        if (document.activeElement === lastElement) {
          e.preventDefault()
          firstElement?.focus()
        }
      }
    }

    container.addEventListener('keydown', handleTab)
    firstElement?.focus()

    return () => {
      container.removeEventListener('keydown', handleTab)
    }
  }, [enabled])

  return containerRef
}

// Skip to main content link
export const SkipToMainContent: React.FC = () => {
  const handleClick = () => {
    const mainContent = document.querySelector('main, [role="main"]')
    if (mainContent) {
      (mainContent as HTMLElement).focus()
      mainContent.scrollIntoView({ behavior: 'smooth' })
    }
  }

  return (
    <a
      href="#main-content"
      onClick={handleClick}
      className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-blue-600 focus:text-white focus:rounded focus:shadow-lg"
      aria-label="Skip to main content"
    >
      Skip to main content
    </a>
  )
}

// ARIA live region for announcements
export const AriaLiveRegion: React.FC<{ priority?: 'polite' | 'assertive' }> = ({ priority = 'polite' }) => {
  return (
    <div
      aria-live={priority}
      aria-atomic="true"
      className="sr-only"
      role="status"
    />
  )
}

// High contrast mode support
export const useHighContrast = () => {
  const [isHighContrast, setIsHighContrast] = useState(false)

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-contrast: high)')
    setIsHighContrast(mediaQuery.matches)

    const handleChange = (e: MediaQueryListEvent) => {
      setIsHighContrast(e.matches)
    }

    mediaQuery.addEventListener('change', handleChange)
    return () => mediaQuery.removeEventListener('change', handleChange)
  }, [])

  useEffect(() => {
    if (isHighContrast) {
      document.documentElement.classList.add('high-contrast')
    } else {
      document.documentElement.classList.remove('high-contrast')
    }
  }, [isHighContrast])

  return isHighContrast
}

// Reduced motion support
export const useReducedMotion = () => {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false)

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
    setPrefersReducedMotion(mediaQuery.matches)

    const handleChange = (e: MediaQueryListEvent) => {
      setPrefersReducedMotion(e.matches)
    }

    mediaQuery.addEventListener('change', handleChange)
    return () => mediaQuery.removeEventListener('change', handleChange)
  }, [])

  useEffect(() => {
    if (prefersReducedMotion) {
      document.documentElement.classList.add('reduced-motion')
    } else {
      document.documentElement.classList.remove('reduced-motion')
    }
  }, [prefersReducedMotion])

  return prefersReducedMotion
}

