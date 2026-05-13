import React from 'react'
import { AppProvider } from './contexts/AppContext'
import { RevIDELayout } from './components/RevIDELayout'
import { ErrorBoundary } from './components/ErrorBoundary'
import { performanceMonitor } from './lib/performance-monitor'
import { productionConfig } from './lib/production-config'

/**
 * Rev's IDE Prototype App
 * 
 * Standalone entry point for Rev's IDE layout prototype.
 * Uses RevIDELayout instead of the standard IDELayout.
 */

function AppRev() {
  // Initialize performance monitoring
  React.useEffect(() => {
    if (productionConfig.monitoring.enableMetrics) {
      performanceMonitor.recordMetric({
        name: 'Rev Prototype Initialization',
        value: Date.now(),
        unit: 'timestamp',
        category: 'render',
        component: 'AppRev',
      })
    }
  }, [])

  return (
    <ErrorBoundary>
      <AppProvider>
        <div className="h-screen flex flex-col overflow-hidden relative bg-gray-900">
          <RevIDELayout theme="dark" />
        </div>
      </AppProvider>
    </ErrorBoundary>
  )
}

export default AppRev

