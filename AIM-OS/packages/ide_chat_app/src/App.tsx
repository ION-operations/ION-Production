import React from 'react'
import { AppProvider } from './contexts/AppContext'
import { TopBar } from './components/TopBar'
import { WaveBackground } from './components/WaveBackground'
import { IDELayout } from './components/IDELayout'
import { ErrorBoundary } from './components/ErrorBoundary'
import { performanceMonitor } from './lib/performance-monitor'
import { productionConfig } from './lib/production-config'

function App() {
  // Initialize performance monitoring
  React.useEffect(() => {
    if (productionConfig.monitoring.enableMetrics) {
      performanceMonitor.recordMetric({
        name: 'App Initialization',
        value: Date.now(),
        unit: 'timestamp',
        category: 'render',
        component: 'App',
      })
    }
  }, [])

  return (
    <ErrorBoundary>
      <AppProvider>
        <div className="h-screen flex flex-col overflow-hidden relative">
          <WaveBackground />
          
          <TopBar />
          
          <IDELayout theme="dark" />
        </div>
      </AppProvider>
    </ErrorBoundary>
  )
}

export default App
