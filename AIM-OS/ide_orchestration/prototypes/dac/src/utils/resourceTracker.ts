// Resource Tracker - Monitor panel memory usage and loading states
// Tracks which panels are mounted, cached, and their resource consumption

import React from 'react'
import { errorTracker } from './errorTracker'

interface PanelResourceInfo {
  id: string
  name: string
  status: 'unloaded' | 'loading' | 'mounted' | 'cached' | 'unmounted'
  mountCount: number
  lastMounted?: Date
  lastUnmounted?: Date
  estimatedMemoryMB: number
  renderCount: number
  loadTime?: number
}

class ResourceTracker {
  private panels: Map<string, PanelResourceInfo> = new Map()
  private performanceObserver?: PerformanceObserver
  
  constructor() {
    this.initializeTracking()
  }
  
  private initializeTracking() {
    // Track when panels are imported (code splitting)
    this.trackLazyImports()
    
    // Monitor performance metrics if available
    if (typeof PerformanceObserver !== 'undefined') {
      try {
        this.performanceObserver = new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            if (entry.name.includes('panel-')) {
              const panelId = entry.name.replace('panel-', '').replace('-start', '').replace('-end', '')
              this.recordLoadTime(panelId, entry.duration)
            }
          }
        })
        this.performanceObserver.observe({ entryTypes: ['measure'] })
      } catch (e) {
        console.warn('PerformanceObserver not supported', e)
      }
    }
  }
  
  private trackLazyImports() {
    // Hook into React.lazy to track when modules are loaded
    const originalLazy = React.lazy
    // Note: This is a simplified approach - in production you'd want more sophisticated tracking
  }
  
  registerPanel(id: string, name: string, estimatedMemoryMB: number = 5) {
    if (!this.panels.has(id)) {
      this.panels.set(id, {
        id,
        name,
        status: 'unloaded',
        mountCount: 0,
        estimatedMemoryMB,
        renderCount: 0
      })
    }
  }
  
  markLoading(id: string) {
    const panel = this.panels.get(id)
    if (panel) {
      panel.status = 'loading'
      if (typeof performance !== 'undefined') {
        performance.mark(`panel-${id}-start`)
      }
    }
  }
  
  markMounted(id: string) {
    const panel = this.panels.get(id)
    if (panel) {
      panel.status = 'mounted'
      panel.mountCount++
      panel.lastMounted = new Date()
      panel.renderCount++
      
      if (typeof performance !== 'undefined') {
        performance.mark(`panel-${id}-end`)
        try {
          performance.measure(`panel-${id}`, `panel-${id}-start`, `panel-${id}-end`)
        } catch (e) {
          // Measure might already exist
        }
      }
      
      // Sync with error tracker
      errorTracker.updatePanelMetrics(id, panel.name, {
        mountCount: panel.mountCount,
        renderCount: panel.renderCount,
        loadTime: panel.loadTime,
        memoryUsage: panel.estimatedMemoryMB
      })
    }
  }
  
  markUnmounted(id: string) {
    const panel = this.panels.get(id)
    if (panel) {
      panel.status = 'cached' // React keeps components cached even when unmounted
      panel.lastUnmounted = new Date()
    }
  }
  
  recordLoadTime(id: string, duration: number) {
    const panel = this.panels.get(id)
    if (panel) {
      panel.loadTime = duration
      
      // Sync with error tracker
      errorTracker.updatePanelMetrics(id, panel.name, {
        mountCount: panel.mountCount,
        renderCount: panel.renderCount,
        loadTime: duration,
        memoryUsage: panel.estimatedMemoryMB
      })
    }
  }
  
  incrementRenderCount(id: string) {
    const panel = this.panels.get(id)
    if (panel) {
      panel.renderCount++
      
      // Sync with error tracker
      errorTracker.updatePanelMetrics(id, panel.name, {
        mountCount: panel.mountCount,
        renderCount: panel.renderCount,
        loadTime: panel.loadTime,
        memoryUsage: panel.estimatedMemoryMB
      })
    }
  }
  
  getPanelInfo(id: string): PanelResourceInfo | undefined {
    return this.panels.get(id)
  }
  
  getAllPanels(): PanelResourceInfo[] {
    return Array.from(this.panels.values())
  }
  
  getMountedPanels(): PanelResourceInfo[] {
    return Array.from(this.panels.values()).filter(p => p.status === 'mounted')
  }
  
  getCachedPanels(): PanelResourceInfo[] {
    return Array.from(this.panels.values()).filter(p => p.status === 'cached')
  }
  
  getTotalEstimatedMemory(): number {
    return Array.from(this.panels.values()).reduce((total, panel) => {
      // Only count mounted and cached panels (loaded into memory)
      if (panel.status === 'mounted' || panel.status === 'cached') {
        return total + panel.estimatedMemoryMB
      }
      return total
    }, 0)
  }
  
  getBrowserMemoryInfo(): { usedJSHeapSize?: number; totalJSHeapSize?: number; jsHeapSizeLimit?: number } {
    if ('memory' in performance) {
      const mem = (performance as any).memory
      return {
        usedJSHeapSize: mem.usedJSHeapSize / 1024 / 1024, // Convert to MB
        totalJSHeapSize: mem.totalJSHeapSize / 1024 / 1024,
        jsHeapSizeLimit: mem.jsHeapSizeLimit / 1024 / 1024
      }
    }
    return {}
  }
  
  cleanup() {
    if (this.performanceObserver) {
      this.performanceObserver.disconnect()
    }
  }
}

// Singleton instance
export const resourceTracker = new ResourceTracker()

// React hook for tracking panel resources
export function usePanelResourceTracking(panelId: string, panelName: string, estimatedMemoryMB: number = 5) {
  React.useEffect(() => {
    resourceTracker.registerPanel(panelId, panelName, estimatedMemoryMB)
    resourceTracker.markLoading(panelId)
    
    return () => {
      resourceTracker.markUnmounted(panelId)
    }
  }, [panelId, panelName, estimatedMemoryMB])
  
  React.useEffect(() => {
    resourceTracker.markMounted(panelId)
  }, [panelId])
  
  React.useEffect(() => {
    resourceTracker.incrementRenderCount(panelId)
  })
}

