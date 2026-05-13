// Panel Registry - Comprehensive registry of all panels in the IDE
// Ensures all panels are tracked for diagnostics, even if not yet mounted

export interface PanelDefinition {
  id: string
  name: string
  category: 'left' | 'right' | 'bottom' | 'main' | 'view'
  component: string // Component name for reference
  estimatedMemoryMB?: number
}

// Comprehensive registry of ALL panels in the IDE
export const PANEL_REGISTRY: PanelDefinition[] = [
  // Left Panels
  { id: 'explorer', name: 'File Explorer', category: 'left', component: 'FileTree', estimatedMemoryMB: 3 },
  { id: 'memory', name: 'Memory Browser', category: 'left', component: 'MemoryBrowser', estimatedMemoryMB: 5 },
  { id: 'status', name: 'System Status', category: 'left', component: 'SystemStatus', estimatedMemoryMB: 2 },
  { id: 'resource-monitor', name: 'Resource Monitor', category: 'left', component: 'ResourceMonitor', estimatedMemoryMB: 4 },
  { id: 'app-preview-controls', name: 'App Preview Controls', category: 'left', component: 'AppPreviewControls', estimatedMemoryMB: 3 },
  { id: 'debug-console', name: 'Debug Console', category: 'left', component: 'DebugConsolePanel', estimatedMemoryMB: 4 },
  
  // Right Panels
  { id: 'context-web', name: 'Context Web', category: 'right', component: 'ContextWeb', estimatedMemoryMB: 8 },
  { id: 'evidence-panel', name: 'Evidence Panel', category: 'right', component: 'EvidencePanel', estimatedMemoryMB: 6 },
  { id: 'timeline', name: 'Timeline View', category: 'right', component: 'TimelineView', estimatedMemoryMB: 6 },
  { id: 'outline', name: 'Code Outline', category: 'right', component: 'OutlinePanel', estimatedMemoryMB: 3 },
  { id: 'ai-chat', name: 'AI Chat', category: 'right', component: 'AIChatManagement', estimatedMemoryMB: 5 },
  { id: 'router', name: 'Router Panel', category: 'right', component: 'RouterPanel', estimatedMemoryMB: 3 },
  { id: 'browser-automation', name: 'Browser Automation', category: 'right', component: 'BrowserAutomationPanel', estimatedMemoryMB: 6 },
  { id: 'lucid-chat', name: 'Lucid Chat', category: 'right', component: 'LucidChatPanel', estimatedMemoryMB: 7 },
  
  // Bottom Panels
  { id: 'terminal', name: 'Terminal', category: 'bottom', component: 'TerminalPanel', estimatedMemoryMB: 4 },
  { id: 'problems', name: 'Problems', category: 'bottom', component: 'ProblemsPanel', estimatedMemoryMB: 3 },
  { id: 'log-sentinels-summaries', name: 'Log Sentinels Summaries', category: 'bottom', component: 'LogSentinelsSummaries', estimatedMemoryMB: 5 },
  { id: 'log-sentinels-anomalies', name: 'Log Sentinels Anomalies', category: 'bottom', component: 'LogSentinelsAnomalies', estimatedMemoryMB: 5 },
  { id: 'tool-quality', name: 'Tool Quality Dashboard', category: 'bottom', component: 'ToolQualityDashboard', estimatedMemoryMB: 6 },
  { id: 'log-analysis', name: 'Log Analysis Dashboard', category: 'bottom', component: 'LogAnalysisDashboard', estimatedMemoryMB: 6 },
  { id: 'context-ledger', name: 'Context Ledger', category: 'bottom', component: 'ContextLedger', estimatedMemoryMB: 4 },
  { id: 'heatmap', name: 'Chat Heatmap', category: 'bottom', component: 'ChatHeatmapPanel', estimatedMemoryMB: 5 },
  
  // Main Views
  { id: 'code', name: 'Code Editor', category: 'main', component: 'CodeEditor', estimatedMemoryMB: 10 },
  { id: 'evolution', name: 'Evolution Explorer', category: 'view', component: 'EvolutionExplorer', estimatedMemoryMB: 8 },
  { id: 'consciousness', name: 'Consciousness Visualization', category: 'view', component: 'ConsciousnessVisualization', estimatedMemoryMB: 12 },
  { id: 'orchestration', name: 'AIM-OS Orchestration', category: 'view', component: 'AIMOSOrchestration', estimatedMemoryMB: 10 },
  { id: 'app-preview', name: 'App Preview', category: 'view', component: 'AppPreview', estimatedMemoryMB: 15 },
  { id: 'document-editor', name: 'Document Editor', category: 'view', component: 'DocumentEditor', estimatedMemoryMB: 8 },
  { id: 'file-preview', name: 'File Preview', category: 'view', component: 'FilePreviewView', estimatedMemoryMB: 6 },
  { id: 'canvas', name: 'Canvas View', category: 'view', component: 'CanvasView', estimatedMemoryMB: 10 },
  { id: 'manager-ai-chat', name: 'Manager AI Chat', category: 'view', component: 'ManagerAIChat', estimatedMemoryMB: 7 },
  
  // Additional Panels
  { id: 'super-index', name: 'Super Index', category: 'right', component: 'SuperIndexPanel', estimatedMemoryMB: 5 },
  { id: 'master-index', name: 'Master Index', category: 'right', component: 'MasterIndexPanel', estimatedMemoryMB: 5 },
  { id: 'system-map', name: 'System Map', category: 'right', component: 'SystemMapPanel', estimatedMemoryMB: 8 },
  { id: 'system-index-browser', name: 'System Index Browser', category: 'right', component: 'SystemIndexBrowserPanel', estimatedMemoryMB: 7 },
  { id: 'nl-tags-explorer', name: 'NL Tags Explorer', category: 'right', component: 'NLTagsExplorerPanel', estimatedMemoryMB: 4 },
  { id: 'documentation-explorer', name: 'Documentation Explorer', category: 'right', component: 'DocumentationExplorerPanel', estimatedMemoryMB: 5 },
  { id: 'organization-systems', name: 'Organization Systems', category: 'right', component: 'OrganizationSystemsPanel', estimatedMemoryMB: 6 },
]

// Helper to get panel definition by ID
export function getPanelDefinition(panelId: string): PanelDefinition | undefined {
  return PANEL_REGISTRY.find(p => p.id === panelId)
}

// Helper to get panel name by ID (with fallback)
export function getPanelName(panelId: string): string {
  const def = getPanelDefinition(panelId)
  return def?.name || panelId.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
}

// Helper to get all panels in a category
export function getPanelsByCategory(category: PanelDefinition['category']): PanelDefinition[] {
  return PANEL_REGISTRY.filter(p => p.category === category)
}

// Helper to get all panel IDs
export function getAllPanelIds(): string[] {
  return PANEL_REGISTRY.map(p => p.id)
}

