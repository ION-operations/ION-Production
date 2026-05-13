// Accessibility Utilities for Max V2
// Provides ARIA attributes, focus management, and screen reader support

import { useRef, useEffect, useCallback } from 'react'

export interface FocusOptions {
  preventScroll?: boolean
  focusVisible?: boolean
}

export const useAccessibility = () => {
  const liveRegionRef = useRef<HTMLDivElement | null>(null)

  // Announce to screen readers
  const announce = useCallback((message: string, priority: 'polite' | 'assertive' = 'polite') => {
    if (!liveRegionRef.current) {
      // Create live region if it doesn't exist
      const liveRegion = document.createElement('div')
      liveRegion.setAttribute('role', 'status')
      liveRegion.setAttribute('aria-live', priority)
      liveRegion.setAttribute('aria-atomic', 'true')
      liveRegion.className = 'sr-only'
      liveRegion.style.cssText = `
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip: rect(0, 0, 0, 0);
        white-space: nowrap;
        border-width: 0;
      `
      document.body.appendChild(liveRegion)
      liveRegionRef.current = liveRegion
    }

    if (liveRegionRef.current) {
      liveRegionRef.current.textContent = message
      // Clear after announcement
      setTimeout(() => {
        if (liveRegionRef.current) {
          liveRegionRef.current.textContent = ''
        }
      }, 1000)
    }
  }, [])

  // Focus management
  const focusElement = useCallback(
    (element: HTMLElement | null, options: FocusOptions = {}) => {
      if (element) {
        element.focus(options)
        if (options.focusVisible !== false) {
          element.classList.add('focus-visible')
        }
      }
    },
    []
  )

  // Trap focus within a container
  const trapFocus = useCallback((container: HTMLElement) => {
    const focusableElements = container.querySelectorAll<HTMLElement>(
      'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
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
    return () => {
      container.removeEventListener('keydown', handleTab)
    }
  }, [])

  // Get ARIA label for panel
  const getPanelAriaLabel = useCallback((panelType: string, panelTitle: string) => {
    return `${panelTitle} panel. Press Escape to close, Arrow keys to navigate.`
  }, [])

  // Get ARIA label for zone
  const getZoneAriaLabel = useCallback((zoneType: string) => {
    const zoneNames: Record<string, string> = {
      top: 'Top bar',
      left: 'Left drawer',
      right: 'Right drawer',
      bottom: 'Bottom drawer',
      center: 'Main content area',
    }
    return `${zoneNames[zoneType] || zoneType} zone`
  }, [])

  return {
    announce,
    focusElement,
    trapFocus,
    getPanelAriaLabel,
    getZoneAriaLabel,
    liveRegionRef,
  }
}

