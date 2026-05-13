// Panel Types
export type PanelZone = 'left' | 'main' | 'right' | 'bottom'

export type PanelType =
  | 'file-explorer'
  | 'memory-browser'
  | 'system-monitor'
  | 'agent-management'
  | 'component-library'
  | 'code-editor'
  | 'context-web'
  | 'evolution-explorer'
  | 'documentation-viewer'
  | 'ui-editor'
  | 'coding-chat'
  | 'planning-chat'
  | 'outline-panel'
  | 'properties-panel'
  | 'search-panel'
  | 'terminal'
  | 'timeline'
  | 'problems'
  | 'debug-console'
  | 'git-panel'

export interface Panel {
  id: string
  type: PanelType
  zone: PanelZone
  title: string
  visible: boolean
  size?: number
  minSize?: number
  maxSize?: number
  order: number
}

export interface Layout {
  id: string
  name: string
  panels: Panel[]
  createdAt: string
  updatedAt: string
}

// AIM-OS Types
export interface CMCAtom {
  id: string
  content: string
  timestamp: string
  tags: string[]
  confidence: number
}

export interface VIFWitness {
  id: string
  task: string
  confidence: number
  evidence: string[]
  timestamp: string
}

export interface TimelineEntry {
  id: string
  prompt_id: string
  user_input: string
  context_state: Record<string, any>
  timestamp: string
}

export interface Agent {
  id: string
  name: string
  status: 'active' | 'idle' | 'busy'
  currentTask: string
  capabilities: string[]
  confidence: number
}

export interface SEGContradiction {
  id: string
  type: 'conflict' | 'inconsistency' | 'error'
  source: string
  target: string
  severity: 'low' | 'medium' | 'high'
  message: string
}

