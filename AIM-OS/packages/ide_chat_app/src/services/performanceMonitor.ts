// Performance Monitoring Service
// V2 Enhancement - Week 3 Integration
// Comprehensive performance tracking and monitoring

import { useState, useEffect, useRef, useCallback } from 'react'

export interface PerformanceMetric {
  id: string
  name: string
  value: number
  unit: string
  timestamp: Date
  category: 'render' | 'memory' | 'network' | 'computation' | 'storage'
  threshold?: {
    warning: number
    error: number
  }
}

export interface PerformanceSnapshot {
  timestamp: Date
  metrics: PerformanceMetric[]
  summary: {
    renderTime: number
    memoryUsage: number
    networkRequests: number
    computationTime: number
  }
}

class PerformanceMonitor {
  private metrics: PerformanceMetric[] = []
  private maxMetrics = 1000
  private observers: Map<string, PerformanceObserver> = new Map()
  private renderTimes: number[] = []
  private networkRequests: number = 0
  private memoryUsage: number[] = []

  constructor() {
    this.initializeObservers()
    this.startMemoryMonitoring()
    this.startRenderMonitoring()
  }

  /**
   * Initialize Performance Observers
   */
  private initializeObservers(): void {
    // Measure render performance
    if ('PerformanceObserver' in window) {
      try {
        const renderObserver = new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            if (entry.entryType === 'measure') {
              this.addMetric({
                id: `render-${Date.now()}`,
                name: entry.name,
                value: entry.duration,
                unit: 'ms',
                timestamp: new Date(),
                category: 'render',
                threshold: {
                  warning: 16.67, // 60fps
                  error: 33.33 // 30fps
                }
              })
            }
          }
        })
        renderObserver.observe({ entryTypes: ['measure'] })
        this.observers.set('render', renderObserver)
      } catch (error) {
        console.warn('Performance Observer not supported:', error)
      }

      // Measure network performance
      try {
        const networkObserver = new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            if (entry.entryType === 'resource') {
              const resourceEntry = entry as PerformanceResourceTiming
              this.networkRequests++
              this.addMetric({
                id: `network-${Date.now()}`,
                name: resourceEntry.name,
                value: resourceEntry.duration,
                unit: 'ms',
                timestamp: new Date(),
                category: 'network',
                threshold: {
                  warning: 1000,
                  error: 3000
                }
              })
            }
          }
        })
        networkObserver.observe({ entryTypes: ['resource'] })
        this.observers.set('network', networkObserver)
      } catch (error) {
        console.warn('Network Observer not supported:', error)
      }
    }
  }

  /**
   * Start memory monitoring
   */
  private startMemoryMonitoring(): void {
    if ('memory' in performance) {
      setInterval(() => {
        const memory = (performance as any).memory
        if (memory) {
          const usedMB = memory.usedJSHeapSize / 1048576
          const totalMB = memory.totalJSHeapSize / 1048576
          const limitMB = memory.jsHeapSizeLimit / 1048576

          this.memoryUsage.push(usedMB)
          if (this.memoryUsage.length > 100) {
            this.memoryUsage.shift()
          }

          this.addMetric({
            id: `memory-${Date.now()}`,
            name: 'Memory Usage',
            value: usedMB,
            unit: 'MB',
            timestamp: new Date(),
            category: 'memory',
            threshold: {
              warning: limitMB * 0.7,
              error: limitMB * 0.9
            }
          })
        }
      }, 5000) // Check every 5 seconds
    }
  }

  /**
   * Start render monitoring
   */
  private startRenderMonitoring(): void {
    let lastFrameTime = performance.now()

    const measureFrame = () => {
      const currentTime = performance.now()
      const frameTime = currentTime - lastFrameTime
      lastFrameTime = currentTime

      this.renderTimes.push(frameTime)
      if (this.renderTimes.length > 60) {
        this.renderTimes.shift()
      }

      requestAnimationFrame(measureFrame)
    }

    requestAnimationFrame(measureFrame)
  }

  /**
   * Add performance metric
   */
  addMetric(metric: PerformanceMetric): void {
    this.metrics.push(metric)
    if (this.metrics.length > this.maxMetrics) {
      this.metrics.shift()
    }
  }

  /**
   * Get current performance snapshot
   */
  getSnapshot(): PerformanceSnapshot {
    const renderTime = this.renderTimes.length > 0
      ? this.renderTimes.reduce((a, b) => a + b, 0) / this.renderTimes.length
      : 0

    const memoryUsage = this.memoryUsage.length > 0
      ? this.memoryUsage[this.memoryUsage.length - 1]
      : 0

    return {
      timestamp: new Date(),
      metrics: [...this.metrics].slice(-100), // Last 100 metrics
      summary: {
        renderTime,
        memoryUsage,
        networkRequests: this.networkRequests,
        computationTime: 0 // TODO: Track computation time
      }
    }
  }

  /**
   * Get metrics by category
   */
  getMetricsByCategory(category: PerformanceMetric['category']): PerformanceMetric[] {
    return this.metrics.filter(m => m.category === category)
  }

  /**
   * Get metrics in time range
   */
  getMetricsInRange(startTime: Date, endTime: Date): PerformanceMetric[] {
    return this.metrics.filter(m => 
      m.timestamp >= startTime && m.timestamp <= endTime
    )
  }

  /**
   * Clear metrics
   */
  clearMetrics(): void {
    this.metrics = []
    this.renderTimes = []
    this.memoryUsage = []
    this.networkRequests = 0
  }

  /**
   * Mark render start
   */
  markRenderStart(componentName: string): void {
    performance.mark(`${componentName}-start`)
  }

  /**
   * Mark render end
   */
  markRenderEnd(componentName: string): void {
    performance.mark(`${componentName}-end`)
    performance.measure(
      `${componentName}-render`,
      `${componentName}-start`,
      `${componentName}-end`
    )
  }

  /**
   * Cleanup
   */
  destroy(): void {
    this.observers.forEach(observer => observer.disconnect())
    this.observers.clear()
    this.clearMetrics()
  }
}

// Singleton instance
let performanceMonitorInstance: PerformanceMonitor | null = null

export function getPerformanceMonitor(): PerformanceMonitor {
  if (!performanceMonitorInstance) {
    performanceMonitorInstance = new PerformanceMonitor()
  }
  return performanceMonitorInstance
}

/**
 * React hook for performance monitoring
 */
export function usePerformanceMonitoring(enabled: boolean = true) {
  const [snapshot, setSnapshot] = useState<PerformanceSnapshot | null>(null)
  const monitorRef = useRef<PerformanceMonitor | null>(null)

  useEffect(() => {
    if (!enabled) return

    monitorRef.current = getPerformanceMonitor()

    const interval = setInterval(() => {
      const newSnapshot = monitorRef.current?.getSnapshot()
      if (newSnapshot) {
        setSnapshot(newSnapshot)
      }
    }, 1000) // Update every second

    return () => {
      clearInterval(interval)
    }
  }, [enabled])

  const markRenderStart = useCallback((componentName: string) => {
    monitorRef.current?.markRenderStart(componentName)
  }, [])

  const markRenderEnd = useCallback((componentName: string) => {
    monitorRef.current?.markRenderEnd(componentName)
  }, [])

  const clearMetrics = useCallback(() => {
    monitorRef.current?.clearMetrics()
    setSnapshot(null)
  }, [])

  return {
    snapshot,
    markRenderStart,
    markRenderEnd,
    clearMetrics
  }
}

