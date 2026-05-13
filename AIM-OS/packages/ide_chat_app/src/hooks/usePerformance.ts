/**
 * Performance Optimization System
 * 
 * Phase 5.2: Performance Optimization
 * 
 * Features:
 * - Lazy loading for components
 * - Virtual scrolling for large lists
 * - Memoization utilities
 * - Debouncing/throttling
 * - Code splitting
 * - Performance monitoring
 */

import { useMemo, useCallback, useEffect, useRef, useState } from 'react'

// Virtual scrolling hook
export interface VirtualScrollOptions {
  itemHeight: number
  containerHeight: number
  overscan?: number
}

export const useVirtualScroll = <T>(
  items: T[],
  options: VirtualScrollOptions
) => {
  const { itemHeight, containerHeight, overscan = 3 } = options
  const [scrollTop, setScrollTop] = useState(0)
  const containerRef = useRef<HTMLDivElement>(null)

  const totalHeight = items.length * itemHeight
  const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan)
  const endIndex = Math.min(
    items.length - 1,
    Math.ceil((scrollTop + containerHeight) / itemHeight) + overscan
  )

  const visibleItems = useMemo(() => {
    return items.slice(startIndex, endIndex + 1).map((item, index) => ({
      item,
      index: startIndex + index,
    }))
  }, [items, startIndex, endIndex])

  const offsetY = startIndex * itemHeight

  const handleScroll = useCallback((e: React.UIEvent<HTMLDivElement>) => {
    setScrollTop(e.currentTarget.scrollTop)
  }, [])

  return {
    containerRef,
    visibleItems,
    totalHeight,
    offsetY,
    handleScroll,
  }
}

// Lazy loading hook
export const useLazyLoad = (
  threshold: number = 0.1,
  rootMargin: string = '100px'
) => {
  const [isVisible, setIsVisible] = useState(false)
  const elementRef = useRef<HTMLElement>(null)

  useEffect(() => {
    const element = elementRef.current
    if (!element) return

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true)
          observer.disconnect()
        }
      },
      {
        threshold,
        rootMargin,
      }
    )

    observer.observe(element)

    return () => {
      observer.disconnect()
    }
  }, [threshold, rootMargin])

  return {
    elementRef,
    isVisible,
  }
}

// Performance monitoring hook
export const usePerformanceMonitor = (componentName: string) => {
  const renderStartTime = useRef<number>(0)
  const renderCount = useRef<number>(0)

  useEffect(() => {
    renderStartTime.current = performance.now()
    renderCount.current += 1

    return () => {
      const renderTime = performance.now() - renderStartTime.current
      if (renderTime > 16) { // > 1 frame (16ms)
        console.warn(`[Performance] ${componentName} render took ${renderTime.toFixed(2)}ms`)
      }
    }
  })

  const measureAsync = useCallback(async <T,>(
    operation: () => Promise<T>,
    operationName: string
  ): Promise<T> => {
    const startTime = performance.now()
    try {
      const result = await operation()
      const duration = performance.now() - startTime
      if (duration > 100) {
        console.warn(`[Performance] ${componentName}.${operationName} took ${duration.toFixed(2)}ms`)
      }
      return result
    } catch (error) {
      const duration = performance.now() - startTime
      console.error(`[Performance] ${componentName}.${operationName} failed after ${duration.toFixed(2)}ms`, error)
      throw error
    }
  }, [componentName])

  return {
    measureAsync,
    renderCount: renderCount.current,
  }
}

// Memoization utilities
export const useStableCallback = <T extends (...args: any[]) => any>(
  callback: T
): T => {
  const callbackRef = useRef(callback)
  callbackRef.current = callback

  return useCallback(
    ((...args: any[]) => callbackRef.current(...args)) as T,
    []
  )
}

// Debounce hook (already exists in useDebounce, but adding for completeness)
export const useDebounce = <T,>(value: T, delay: number): T => {
  const [debouncedValue, setDebouncedValue] = useState<T>(value)

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value)
    }, delay)

    return () => {
      clearTimeout(handler)
    }
  }, [value, delay])

  return debouncedValue
}

// Throttle hook
export const useThrottle = <T,>(value: T, delay: number): T => {
  const [throttledValue, setThrottledValue] = useState<T>(value)
  const lastRun = useRef<number>(Date.now())

  useEffect(() => {
    const handler = setTimeout(() => {
      if (Date.now() - lastRun.current >= delay) {
        setThrottledValue(value)
        lastRun.current = Date.now()
      }
    }, delay - (Date.now() - lastRun.current))

    return () => {
      clearTimeout(handler)
    }
  }, [value, delay])

  return throttledValue
}

// Code splitting helper
export const lazyLoadComponent = <T extends React.ComponentType<any>>(
  importFunc: () => Promise<{ default: T }>
): React.LazyExoticComponent<T> => {
  return React.lazy(importFunc)
}

// Import React for component usage
import React from 'react'

