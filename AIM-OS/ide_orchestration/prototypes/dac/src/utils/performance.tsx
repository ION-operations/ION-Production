// Performance Optimization Utilities - V2 Foundation Enhancement
// Memoization helpers, lazy loading wrappers, and render optimization utilities

import React, { ComponentType, lazy, Suspense, memo, useMemo, useCallback } from 'react'
import { Loader2 } from 'lucide-react'
import { getPanelName, getPanelDefinition, PANEL_REGISTRY } from './panelRegistry'

// Map component names to panel IDs for auto-detection
const COMPONENT_TO_PANEL_ID: Record<string, string> = {
  'LazyFileTree': 'explorer',
  'LazyMemoryBrowser': 'memory',
  'LazySystemStatus': 'status',
  'LazyResourceMonitor': 'resource-monitor',
  'LazyAppPreviewControls': 'app-preview-controls',
  'LazyDebugConsolePanel': 'debug-console',
  'LazyContextWeb': 'context-web',
  'LazyTimelineView': 'timeline',
  'LazyOutlinePanel': 'outline',
  'LazyAIChatManagement': 'ai-chat',
  'LazyRouterPanel': 'router',
  'LazyBrowserAutomationPanel': 'browser-automation',
  'LazyTerminalPanel': 'terminal',
  'LazyProblemsPanel': 'problems',
  'LazyLogSentinelsSummaries': 'log-sentinels-summaries',
  'LazyLogSentinelsAnomalies': 'log-sentinels-anomalies',
  'LazyToolQualityDashboard': 'tool-quality',
  'LazyLogAnalysisDashboard': 'log-analysis',
  'LazyContextLedger': 'context-ledger',
  'LazyChatHeatmapPanel': 'heatmap',
  'LazyCodeEditor': 'code',
  'LazyEvolutionExplorer': 'evolution',
  'LazyConsciousnessVisualization': 'consciousness',
  'LazyAIMOSOrchestration': 'orchestration',
  'LazyAppPreview': 'app-preview',
  'LazyDocumentEditor': 'document-editor',
  'LazyFilePreviewView': 'file-preview',
  'LazyCanvasView': 'canvas',
  'LazyManagerAIChat': 'manager-ai-chat',
  'LazyBackendDesign': 'backend-design',
  'LazySuperIndexPanel': 'super-index',
  'LazyMasterIndexPanel': 'master-index',
  'LazySystemMapPanel': 'system-map',
  'LazySystemIndexBrowserPanel': 'system-index-browser',
  'LazyNLTagsExplorerPanel': 'nl-tags-explorer',
  'LazyDocumentationExplorerPanel': 'documentation-explorer',
}

// ===== LAZY LOADING =====

// Lazy load panel components for code splitting
export const LazyFileTree = lazy(() => import('../panels/FileTree').then(m => ({ default: m.FileTree })))
export const LazyMemoryBrowser = lazy(() => import('../panels/MemoryBrowser').then(m => ({ default: m.MemoryBrowser })))
export const LazySystemStatus = lazy(() => import('../panels/SystemStatus').then(m => ({ default: m.SystemStatus })))
export const LazyContextWeb = lazy(() => import('../panels/ContextWeb').then(m => ({ default: m.ContextWeb })))
export const LazyTimelineView = lazy(() => import('../panels/TimelineView').then(m => ({ default: m.TimelineView })))
export const LazyCodeEditor = lazy(() => import('../panels/CodeEditor').then(m => ({ default: m.CodeEditor })))
export const LazyTerminalPanel = lazy(() => import('../panels/TerminalPanel').then(m => ({ default: m.TerminalPanel })))
export const LazyOutlinePanel = lazy(() => import('../panels/OutlinePanel').then(m => ({ default: m.OutlinePanel })))
export const LazyProblemsPanel = lazy(() => import('../panels/ProblemsPanel').then(m => ({ default: m.ProblemsPanel })))
export const LazyDebugConsolePanel = lazy(() => import('../panels/DebugConsolePanel').then(m => ({ default: m.DebugConsolePanel })))
export const LazySuperIndexPanel = lazy(() => import('../panels/SuperIndexPanel').then(m => ({ default: m.SuperIndexPanel })))
export const LazyMasterIndexPanel = lazy(() => import('../panels/MasterIndexPanel').then(m => ({ default: m.MasterIndexPanel })))
export const LazySystemMapPanel = lazy(() => import('../panels/SystemMapPanel').then(m => ({ default: m.SystemMapPanel })))
export const LazySystemIndexBrowserPanel = lazy(() => import('../panels/SystemIndexBrowserPanel').then(m => ({ default: m.SystemIndexBrowserPanel })))
export const LazyNLTagsExplorerPanel = lazy(() => import('../panels/NLTagsExplorerPanel').then(m => ({ default: m.NLTagsExplorerPanel })))
export const LazyDocumentationExplorerPanel = lazy(() => import('../panels/DocumentationExplorerPanel').then(m => ({ default: m.DocumentationExplorerPanel })))
export const LazyEvolutionExplorer = lazy(() => import('../views/EvolutionExplorer').then(m => ({ default: m.EvolutionExplorer })))
export const LazyConsciousnessVisualization = lazy(() => import('../views/ConsciousnessVisualization').then(m => ({ default: m.ConsciousnessVisualization })))
export const LazyAIMOSOrchestration = lazy(() => import('../views/AIMOSOrchestration').then(m => ({ default: m.AIMOSOrchestration })))
export const LazyAppPreview = lazy(() => import('../views/AppPreview').then(m => ({ default: m.AppPreview })))
export const LazyAppPreviewControls = lazy(() => import('../panels/AppPreviewControls').then(m => ({ default: m.AppPreviewControls })))
export const LazyAIChatManagement = lazy(() => import('../panels/AIChatManagement').then(m => ({ default: m.default || m.AIChatManagement })))
export const LazyChatHeatmapPanel = lazy(() => import('../components/ChatHeatmapPanel').then(m => ({ default: m.ChatHeatmapPanel })))
export const LazyContextLedger = lazy(() => import('../components/ContextLedger').then(m => ({ default: m.ContextLedger })))
export const LazyRouterPanel = lazy(() => import('../panels/RouterPanel').then(m => ({ default: m.RouterPanel })))
export const LazyLogSentinelsSummaries = lazy(() => import('../panels/LogSentinelsSummaries').then(m => ({ default: m.LogSentinelsSummaries })))
export const LazyLogSentinelsAnomalies = lazy(() => import('../panels/LogSentinelsAnomalies').then(m => ({ default: m.LogSentinelsAnomalies })))
export const LazyToolQualityDashboard = lazy(() => import('../panels/ToolQualityDashboard').then(m => ({ default: m.ToolQualityDashboard })))
export const LazyDocumentEditor = lazy(() => import('../panels/DocumentEditor').then(m => ({ default: m.DocumentEditor })))
export const LazyResourceMonitor = lazy(() => import('../panels/ResourceMonitor').then(m => ({ default: m.ResourceMonitor })))
export const LazyLogAnalysisDashboard = lazy(() => import('../panels/LogAnalysisDashboard').then(m => ({ default: m.LogAnalysisDashboard })))
export const LazyBrowserAutomationPanel = lazy(() => import('../panels/BrowserAutomationPanel').then(m => ({ default: m.BrowserAutomationPanel })))
export const LazyFilePreviewView = lazy(() => import('../views/FilePreviewView').then(m => ({ default: m.FilePreviewView })))
export const LazyCanvasView = lazy(() => import('../views/CanvasView').then(m => ({ default: m.CanvasView })))
export const LazyManagerAIChat = lazy(() => import('../components/ManagerAIChat').then(m => ({ default: m.ManagerAIChat })))
export const LazyBackendDesign = lazy(() => import('../views/BackendDesignView').then(m => ({ default: m.BackendDesignView })))

// Loading fallback component
const PanelLoadingFallback: React.FC = () => (
  <div className="flex items-center justify-center h-full">
    <Loader2 className="w-6 h-6 animate-spin text-blue-400" />
  </div>
)

// Suspense wrapper for lazy-loaded panels with resource tracking
export const LazyPanelWrapper: React.FC<{ 
  children: React.ReactNode
  panelId?: string
  panelName?: string
  autoDetectId?: boolean // Auto-detect panel ID from component name
}> = ({ 
  children, 
  panelId,
  panelName,
  autoDetectId = true
}) => {
  // Auto-detect panel ID from component name if not provided
  const detectedPanelId = React.useMemo(() => {
    if (panelId) return panelId
    
    if (autoDetectId && React.isValidElement(children)) {
      const componentName = (children.type as any)?.displayName || (children.type as any)?.name || ''
      
      // Try direct mapping first
      if (componentName && COMPONENT_TO_PANEL_ID[componentName]) {
        return COMPONENT_TO_PANEL_ID[componentName]
      }
      
      // Fallback: convert component names like "LazyCodeEditor" to "code-editor"
      if (componentName) {
        const normalized = componentName
          .replace(/^Lazy/, '')
          .replace(/Panel$/, '')
          .replace(/View$/, '')
          .replace(/([A-Z])/g, '-$1')
          .toLowerCase()
          .replace(/^-/, '')
        
        // Check if normalized ID exists in registry
        if (PANEL_REGISTRY.some(p => p.id === normalized)) {
          return normalized
        }
      }
    }
    
    return 'unknown-panel'
  }, [panelId, children, autoDetectId])
  
  const finalPanelName = React.useMemo(() => {
    if (panelName) return panelName
    return getPanelName(detectedPanelId)
  }, [panelName, detectedPanelId])
  
  // Track panel loading if ID provided
  React.useEffect(() => {
    if (detectedPanelId && finalPanelName) {
      // Import resource tracker dynamically to avoid circular deps
      import('./resourceTracker').then(({ resourceTracker }) => {
        const panelDef = getPanelDefinition(detectedPanelId)
        const estimatedMemory = panelDef?.estimatedMemoryMB || 5
        resourceTracker.registerPanel(detectedPanelId, finalPanelName, estimatedMemory)
        resourceTracker.markLoading(detectedPanelId)
      })
      
      // Also register with error tracker
      import('./errorTracker').then(({ errorTracker }) => {
        errorTracker.getOrCreateDiagnostics(detectedPanelId, finalPanelName)
      })
    }
  }, [detectedPanelId, finalPanelName])
  
  React.useEffect(() => {
    if (detectedPanelId) {
      import('./resourceTracker').then(({ resourceTracker }) => {
        resourceTracker.markMounted(detectedPanelId)
      })
    }
    
    return () => {
      if (detectedPanelId) {
        import('./resourceTracker').then(({ resourceTracker }) => {
          resourceTracker.markUnmounted(detectedPanelId)
        })
      }
    }
  }, [detectedPanelId])
  
  return (
    <Suspense fallback={<PanelLoadingFallback />}>
      {children}
    </Suspense>
  )
}

// ===== MEMOIZATION HELPERS =====

// Memoize component with custom comparison function
export function memoWithComparison<T extends ComponentType<any>>(
  Component: T,
  areEqual?: (prevProps: React.ComponentProps<T>, nextProps: React.ComponentProps<T>) => boolean
): React.MemoExoticComponent<T> {
  return memo(Component, areEqual)
}

// Memoize expensive computations
export function useExpensiveComputation<T>(
  computeFn: () => T,
  deps: React.DependencyList
): T {
  return useMemo(computeFn, deps)
}

// Memoize event handlers
export function useStableCallback<T extends (...args: any[]) => any>(
  callback: T,
  deps: React.DependencyList
): T {
  return useCallback(callback, deps) as T
}

// ===== RENDER OPTIMIZATION =====

// Conditional render wrapper to prevent unnecessary renders
export const ConditionalRender: React.FC<{
  condition: boolean
  children: React.ReactNode
  fallback?: React.ReactNode
}> = memo(({ condition, children, fallback = null }) => {
  return condition ? <>{children}</> : <>{fallback}</>
})

ConditionalRender.displayName = 'ConditionalRender'

// Panel visibility wrapper
export const VisiblePanel: React.FC<{
  visible: boolean
  children: React.ReactNode
}> = memo(({ visible, children }) => {
  if (!visible) return null
  return <>{children}</>
})

VisiblePanel.displayName = 'VisiblePanel'

// ===== PERFORMANCE MONITORING =====

// Performance measurement hook
export function usePerformanceMeasure(label: string) {
  return useCallback(() => {
    if (typeof performance !== 'undefined' && performance.mark) {
      performance.mark(`${label}-start`)
      return () => {
        performance.mark(`${label}-end`)
        performance.measure(label, `${label}-start`, `${label}-end`)
      }
    }
    return () => {}
  }, [label])
}

// Render count tracking (development only)
export function useRenderCount(componentName: string) {
  const countRef = React.useRef(0)
  countRef.current++
  
  if (process.env.NODE_ENV === 'development') {
    console.log(`[Render] ${componentName}: ${countRef.current}`)
  }
  
  return countRef.current
}

// ===== OPTIMIZED PANEL COMPONENT WRAPPER =====

interface OptimizedPanelProps {
  id: string
  visible: boolean
  children: React.ReactNode
  lazy?: boolean
}

export const OptimizedPanel: React.FC<OptimizedPanelProps> = memo(({ id, visible, children, lazy = false }) => {
  useRenderCount(`OptimizedPanel-${id}`)
  
  if (!visible) return null
  
  if (lazy) {
    return (
      <LazyPanelWrapper>
        {children}
      </LazyPanelWrapper>
    )
  }
  
  return <>{children}</>
}, (prevProps, nextProps) => {
  // Only re-render if visibility changes or id changes
  return prevProps.visible === nextProps.visible && prevProps.id === nextProps.id
})

OptimizedPanel.displayName = 'OptimizedPanel'

